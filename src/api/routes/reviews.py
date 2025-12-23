"""Code review endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import defaultdict
from src.core.schemas import (
    ReviewRequest,
    ReviewResponse,
    AgentType,
    Issue,
    Severity,
    AgentResult,
)
from src.core.orchestrator import AgentOrchestrator
from src.integrations.github import GitHubIntegration
from src.database.connection import get_db
from src.database.models import Review, Repository, ReviewResult
from sqlalchemy import func, desc

router = APIRouter()
orchestrator = AgentOrchestrator()

import logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


@router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    request: ReviewRequest,
    db: Session = Depends(get_db),
):
    """Create a new code review.

    Args:
        request: Review request
        db: Database session

    Returns:
        Review response
    """
    try:
        # Get or create repository
        repo = db.query(Repository).filter(Repository.url == request.repository_url).first()
        if not repo:
            # Extract platform and owner from URL
            if "github.com" in request.repository_url:
                platform = "github"
                parts = request.repository_url.replace("https://github.com/", "").split("/")
                owner = parts[0] if parts else "unknown"
                name = parts[1].replace(".git", "") if len(parts) > 1 else "unknown"
            elif "gitlab.com" in request.repository_url:
                platform = "gitlab"
                parts = request.repository_url.replace("https://gitlab.com/", "").split("/")
                owner = parts[0] if parts else "unknown"
                name = parts[1].replace(".git", "") if len(parts) > 1 else "unknown"
            else:
                platform = "unknown"
                owner = "unknown"
                name = "unknown"

            repo = Repository(
                name=name,
                url=request.repository_url,
                platform=platform,
                owner=owner,
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)

        # Fetch code from GitHub/GitLab or local file
        code = ""
        file_path = request.file_path or "unknown"

        try:
            # Check if it's a local file path (doesn't start with http)
            if request.file_path and not request.repository_url.startswith("http"):
                # Local file - read directly
                import os
                if os.path.exists(request.file_path):
                    with open(request.file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    file_path = request.file_path
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Local file not found: {request.file_path}"
                    )
            elif request.repository_url and request.repository_url.startswith("http"):
                # GitHub/GitLab repository - use integration
                github = GitHubIntegration()
                
                # Check if user wants to scan entire repository
                if request.scan_entire_repo:
                    # Scan entire repository for all Python files
                    all_files = github.get_all_python_files(request.repository_url, request.commit_sha)
                    if not all_files:
                        raise HTTPException(
                            status_code=404,
                            detail="No Python files found in repository."
                        )
                    
                    # Limit number of files for very large repositories (performance)
                    max_files = 50  # Limit to first 50 files to avoid timeout
                    total_files_found = len(all_files)
                    if len(all_files) > max_files:
                        logger.warning(f"Repository has {total_files_found} Python files. Processing first {max_files} files.")
                        all_files = all_files[:max_files]
                    
                    # Process all files
                    all_results = []
                    total_issues = 0
                    
                    # Create a review record for the entire repository scan
                    if total_files_found > max_files:
                        file_path_display = f"Repository scan ({max_files}/{total_files_found} files)"
                    else:
                        file_path_display = f"Repository scan ({len(all_files)} files)"
                    
                    review = Review(
                        repository_id=repo.id,
                        commit_sha=request.commit_sha,
                        pull_request_id=request.pull_request_id,
                        file_path=file_path_display,
                        status="pending",
                    )
                    db.add(review)
                    db.commit()
                    db.refresh(review)
                    
                    # Initialize aggregated results by agent type
                    agent_results_dict = {}
                    
                    # Process each file
                    logger.info(f"Starting repository scan: {len(all_files)} files to process")
                    for idx, file_info in enumerate(all_files, 1):
                        logger.info(f"Processing file {idx}/{len(all_files)}: {file_info['path']}")
                        file_code = file_info["content"]
                        file_path_item = file_info["path"]
                        
                        # Run agents for this file
                        agent_types = request.agent_types or None
                        file_results = await orchestrator.review_code(file_code, file_path_item, agent_types)
                        
                        # Save results to database and aggregate
                        for result in file_results:
                            # Add file path to each issue
                            for issue in result.issues:
                                # Update issue message to include file path at the beginning
                                # Format: [file_path] original message
                                issue_message = issue.message
                                if not issue_message.startswith(f"[{file_path_item}]"):
                                    issue_message = f"[{file_path_item}] {issue_message}"
                                
                                # Ensure file_path is in metadata
                                issue_metadata = issue.metadata.copy() if issue.metadata else {}
                                issue_metadata["file_path"] = file_path_item
                                
                                issue_with_path = Issue(
                                    severity=issue.severity,
                                    issue_type=issue.issue_type,
                                    message=issue_message,
                                    line_number=issue.line_number,
                                    suggestion=issue.suggestion,
                                    metadata=issue_metadata,
                                )
                                
                                # Save to database
                                db_result = ReviewResult(
                                    review_id=review.id,
                                    agent_type=result.agent_type.value,
                                    severity=issue.severity.value,
                                    issue_type=issue.issue_type,
                                    message=issue_with_path.message,
                                    line_number=issue.line_number,
                                    suggestion=issue.suggestion,
                                    meta_data=issue_with_path.metadata,
                                )
                                db.add(db_result)
                                total_issues += 1
                                
                                # Aggregate by agent type
                                if result.agent_type not in agent_results_dict:
                                    agent_results_dict[result.agent_type] = {
                                        "issues": [],
                                        "total_time": 0.0,
                                        "success": True,
                                    }
                                
                                agent_results_dict[result.agent_type]["issues"].append(issue_with_path)
                                agent_results_dict[result.agent_type]["total_time"] += result.execution_time
                                if not result.success:
                                    agent_results_dict[result.agent_type]["success"] = False
                    
                    # Convert aggregated results to AgentResult list
                    for agent_type, data in agent_results_dict.items():
                        all_results.append(
                            AgentResult(
                                agent_type=agent_type,
                                success=data["success"],
                                execution_time=data["total_time"],
                                issues=data["issues"],
                            )
                        )
                    
                    # Update review status
                    review.status = "completed"
                    review.completed_at = datetime.utcnow()
                    db.commit()
                    
                    # Update file_path to show total vs processed
                    if total_files_found > max_files:
                        file_path_display = f"Repository scan ({max_files}/{total_files_found} files processed)"
                    else:
                        file_path_display = f"Repository scan ({len(all_files)} files)"
                    
                    return ReviewResponse(
                        review_id=review.id,
                        repository_url=request.repository_url,
                        file_path=file_path_display,
                        status="completed",
                        results=all_results,
                        total_issues=total_issues,
                        created_at=review.created_at,
                        completed_at=review.completed_at,
                    )
                
                # Priority: file_path > commit_sha > pull_request_id
                # Only use PR/Commit if file_path is not provided
                elif request.file_path and request.file_path.strip():
                    file_path_input = request.file_path.strip()
                    
                    # Check if file_path is a directory (doesn't end with .py)
                    # If it's a directory, scan all Python files in that directory
                    if not file_path_input.endswith('.py'):
                        # It's a directory - get all Python files in that directory
                        try:
                            all_files = github.get_python_files_in_directory(
                                request.repository_url, 
                                file_path_input, 
                                request.commit_sha
                            )
                            
                            if not all_files:
                                raise HTTPException(
                                    status_code=404,
                                    detail=f"No Python files found in directory '{file_path_input}'."
                                )
                            
                            # Limit number of files for very large directories (performance)
                            max_files = 50  # Limit to first 50 files to avoid timeout
                            total_files_found = len(all_files)
                            if len(all_files) > max_files:
                                logger.warning(f"Directory '{file_path_input}' has {total_files_found} Python files. Processing first {max_files} files.")
                                all_files = all_files[:max_files]
                            
                            # Process all files in the directory
                            all_results = []
                            total_issues = 0
                            
                            # Create a review record for the directory scan
                            if total_files_found > max_files:
                                file_path_display = f"Directory scan: {file_path_input} ({max_files}/{total_files_found} files processed)"
                            else:
                                file_path_display = f"Directory scan: {file_path_input} ({len(all_files)} files)"
                            
                            review = Review(
                                repository_id=repo.id,
                                commit_sha=request.commit_sha,
                                pull_request_id=request.pull_request_id,
                                file_path=file_path_display,
                                status="pending",
                            )
                            db.add(review)
                            db.commit()
                            db.refresh(review)
                            
                            # Initialize aggregated results by agent type
                            agent_results_dict = {}
                            
                            # Process each file
                            logger.info(f"Starting directory scan: {len(all_files)} files to process in '{file_path_input}'")
                            for idx, file_info in enumerate(all_files, 1):
                                logger.info(f"Processing file {idx}/{len(all_files)}: {file_info['path']}")
                                file_code = file_info["content"]
                                file_path_item = file_info["path"]
                                
                                # Run agents for this file
                                agent_types = request.agent_types or None
                                file_results = await orchestrator.review_code(file_code, file_path_item, agent_types)
                                
                                # Save results to database and aggregate
                                for result in file_results:
                                    # Add file path to each issue
                                    for issue in result.issues:
                                        # Update issue message to include file path at the beginning
                                        # Format: [file_path] original message
                                        issue_message = issue.message
                                        if not issue_message.startswith(f"[{file_path_item}]"):
                                            issue_message = f"[{file_path_item}] {issue_message}"
                                        
                                        # Ensure file_path is in metadata
                                        issue_metadata = issue.metadata.copy() if issue.metadata else {}
                                        issue_metadata["file_path"] = file_path_item
                                        
                                        issue_with_path = Issue(
                                            severity=issue.severity,
                                            issue_type=issue.issue_type,
                                            message=issue_message,
                                            line_number=issue.line_number,
                                            suggestion=issue.suggestion,
                                            metadata=issue_metadata,
                                        )
                                        
                                        # Save to database
                                        db_result = ReviewResult(
                                            review_id=review.id,
                                            agent_type=result.agent_type.value,
                                            severity=issue.severity.value,
                                            issue_type=issue.issue_type,
                                            message=issue_with_path.message,
                                            line_number=issue.line_number,
                                            suggestion=issue.suggestion,
                                            meta_data=issue_with_path.metadata,
                                        )
                                        db.add(db_result)
                                        total_issues += 1
                                        
                                        # Aggregate by agent type
                                        if result.agent_type not in agent_results_dict:
                                            agent_results_dict[result.agent_type] = {
                                                "issues": [],
                                                "total_time": 0.0,
                                                "success": True,
                                            }
                                        
                                        agent_results_dict[result.agent_type]["issues"].append(issue_with_path)
                                        agent_results_dict[result.agent_type]["total_time"] += result.execution_time
                                        if not result.success:
                                            agent_results_dict[result.agent_type]["success"] = False
                            
                            # Convert aggregated results to AgentResult list
                            for agent_type, data in agent_results_dict.items():
                                all_results.append(
                                    AgentResult(
                                        agent_type=agent_type,
                                        success=data["success"],
                                        execution_time=data["total_time"],
                                        issues=data["issues"],
                                    )
                                )
                            
                            # Update review status
                            review.status = "completed"
                            review.completed_at = datetime.utcnow()
                            db.commit()
                            
                            return ReviewResponse(
                                review_id=review.id,
                                repository_url=request.repository_url,
                                file_path=file_path_display,
                                status="completed",
                                results=all_results,
                                total_issues=total_issues,
                                created_at=review.created_at,
                                completed_at=review.completed_at,
                            )
                            
                        except ValueError as e:
                            # Re-raise ValueError as HTTPException with better message
                            raise HTTPException(status_code=404, detail=str(e))
                    else:
                        # It's a single file - get file content
                        try:
                            code = github.get_file_content(request.repository_url, file_path_input, request.commit_sha)
                            if not code or not code.strip():
                                raise HTTPException(
                                    status_code=404,
                                    detail=f"File '{file_path_input}' is empty or could not be read from repository."
                                )
                            file_path = file_path_input
                        except ValueError as e:
                            # Re-raise ValueError as HTTPException with better message
                            raise HTTPException(status_code=404, detail=str(e))
                elif request.commit_sha and request.commit_sha.strip():
                    # Commit SHA - get files from commit
                    files = github.get_commit_files(request.repository_url, request.commit_sha)
                    if files:
                        code = files[0]["content"]
                        file_path = files[0]["path"]
                    else:
                        raise HTTPException(
                            status_code=404,
                            detail=f"No Python files found in commit {request.commit_sha}"
                        )
                elif request.pull_request_id and request.pull_request_id > 0:
                    # Pull Request - get files from PR (only if file_path is not provided)
                    try:
                        files = github.get_pull_request_files(request.repository_url, request.pull_request_id)
                        if files:
                            code = files[0]["content"]
                            file_path = files[0]["path"]
                        else:
                            raise HTTPException(
                                status_code=404,
                                detail=f"No Python files found in pull request #{request.pull_request_id}. Please use file_path instead."
                            )
                    except Exception as e:
                        # If PR not found, provide helpful error message
                        error_msg = str(e)
                        if "404" in error_msg or "Not Found" in error_msg:
                            raise HTTPException(
                                status_code=404,
                                detail=f"Pull request #{request.pull_request_id} not found in this repository. Please check the PR number or use 'file_path' field instead (leave PR ID empty)."
                            )
                        raise
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="For GitHub/GitLab repositories, please provide either: (1) file_path, or (2) commit_sha, or (3) pull_request_id. Leave other fields empty."
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Must provide either a local file_path or a repository_url with file_path/commit_sha/pull_request_id"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching code: {str(e)}")

        # Create review record
        review = Review(
            repository_id=repo.id,
            commit_sha=request.commit_sha,
            pull_request_id=request.pull_request_id,
            file_path=file_path,
            status="pending",
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        # Run agents
        agent_types = request.agent_types or None
        results = await orchestrator.review_code(code, file_path, agent_types)

        # Save results to database
        total_issues = 0
        for result in results:
            for issue in result.issues:
                # Add file path to issue message and metadata for single file reviews
                issue_message = issue.message
                if not issue_message.startswith(f"[{file_path}]"):
                    issue_message = f"[{file_path}] {issue_message}"
                
                issue_metadata = issue.metadata.copy() if issue.metadata else {}
                issue_metadata["file_path"] = file_path
                
                db_result = ReviewResult(
                    review_id=review.id,
                    agent_type=result.agent_type.value,
                    severity=issue.severity.value,
                    issue_type=issue.issue_type,
                    message=issue_message,
                    line_number=issue.line_number,
                    suggestion=issue.suggestion,
                    meta_data=issue_metadata,
                )
                db.add(db_result)
                total_issues += 1
                
                # Update issue object for response (add file path)
                issue.message = issue_message
                issue.metadata = issue_metadata

        # Update review status
        review.status = "completed"
        review.completed_at = datetime.utcnow()
        db.commit()

        return ReviewResponse(
            review_id=review.id,
            repository_url=request.repository_url,
            file_path=file_path,
            status="completed",
            results=results,
            total_issues=total_issues,
            created_at=review.created_at,
            completed_at=review.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """Get all reviews.

    Args:
        limit: Maximum number of reviews to return
        offset: Number of reviews to skip
        db: Database session

    Returns:
        List of review responses
    """
    reviews = db.query(Review).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    result_list = []
    for review in reviews:
        # Get results
        db_results = db.query(ReviewResult).filter(ReviewResult.review_id == review.id).all()

        # Group results by agent type
        agent_results = defaultdict(list)

        for db_result in db_results:
            issue = Issue(
                severity=Severity(db_result.severity),
                issue_type=db_result.issue_type,
                message=db_result.message,
                line_number=db_result.line_number,
                suggestion=db_result.suggestion,
                metadata=db_result.meta_data,
            )
            agent_results[db_result.agent_type].append(issue)

        # Build response
        results = []
        for agent_type, issues in agent_results.items():
            results.append(
                AgentResult(
                    agent_type=AgentType(agent_type),
                    success=True,
                    execution_time=0.0,
                    issues=issues,
                )
            )

        repo = db.query(Repository).filter(Repository.id == review.repository_id).first()

        result_list.append(
            ReviewResponse(
                review_id=review.id,
                repository_url=repo.url if repo else "",
                file_path=review.file_path,
                status=review.status,
                results=results,
                total_issues=len(db_results),
                created_at=review.created_at,
                completed_at=review.completed_at,
            )
        )
    
    return result_list


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get review by ID.

    Args:
        review_id: Review ID
        db: Database session

    Returns:
        Review response
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Get results
    db_results = db.query(ReviewResult).filter(ReviewResult.review_id == review_id).all()

    # Group results by agent type
    agent_results = defaultdict(list)

    for db_result in db_results:
        issue = Issue(
            severity=Severity(db_result.severity),
            issue_type=db_result.issue_type,
            message=db_result.message,
            line_number=db_result.line_number,
            suggestion=db_result.suggestion,
            metadata=db_result.meta_data,  # Map meta_data back to metadata in response
        )
        agent_results[db_result.agent_type].append(issue)

    # Build response
    results = []
    for agent_type, issues in agent_results.items():
        results.append(
            AgentResult(
                agent_type=AgentType(agent_type),
                success=True,
                execution_time=0.0,  # Not stored in DB
                issues=issues,
            )
        )

    repo = db.query(Repository).filter(Repository.id == review.repository_id).first()

    return ReviewResponse(
        review_id=review.id,
        repository_url=repo.url if repo else "",
        file_path=review.file_path,
        status=review.status,
        results=results,
        total_issues=len(db_results),
        created_at=review.created_at,
        completed_at=review.completed_at,
    )


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics and metrics.

    Args:
        db: Database session

    Returns:
        Dictionary with analytics data
    """
    # Total reviews
    total_reviews = db.query(Review).count()
    
    # Total issues
    total_issues = db.query(ReviewResult).count()
    
    # Completed reviews
    completed_reviews = db.query(Review).filter(Review.status == "completed").count()
    
    # Success rate
    success_rate = (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Average issues per review
    # Get count of issues per review, then calculate average
    issue_counts = db.query(
        ReviewResult.review_id,
        func.count(ReviewResult.id).label('count')
    ).group_by(ReviewResult.review_id).all()
    
    avg_issues = sum(count for _, count in issue_counts) / len(issue_counts) if issue_counts else 0
    
    # Issues by severity
    severity_counts = db.query(
        ReviewResult.severity,
        func.count(ReviewResult.id).label('count')
    ).group_by(ReviewResult.severity).all()
    
    severity_stats = {severity: count for severity, count in severity_counts}
    
    # Issues by agent type
    agent_counts = db.query(
        ReviewResult.agent_type,
        func.count(ReviewResult.id).label('count')
    ).group_by(ReviewResult.agent_type).all()
    
    agent_stats = {agent_type: count for agent_type, count in agent_counts}
    
    # Reviews by repository
    repo_counts = db.query(
        Repository.url,
        func.count(Review.id).label('count')
    ).join(Review).group_by(Repository.url).order_by(desc('count')).limit(10).all()
    
    repo_stats = [{"url": url, "count": count} for url, count in repo_counts]
    
    # Recent reviews (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_reviews = db.query(Review).filter(Review.created_at >= seven_days_ago).count()
    
    return {
        "total_reviews": total_reviews,
        "total_issues": total_issues,
        "completed_reviews": completed_reviews,
        "success_rate": round(success_rate, 2),
        "avg_issues_per_review": round(avg_issues, 2),
        "severity_stats": severity_stats,
        "agent_stats": agent_stats,
        "repo_stats": repo_stats,
        "recent_reviews": recent_reviews,
    }


@router.delete("/reviews")
async def clear_all_reviews(db: Session = Depends(get_db)):
    """Clear all reviews and related data.

    Args:
        db: Database session

    Returns:
        Success message
    """
    try:
        # Delete all review results first (foreign key constraint)
        deleted_results = db.query(ReviewResult).delete()
        
        # Delete all reviews
        deleted_reviews = db.query(Review).delete()
        
        # Optionally delete repositories that have no reviews
        # (or keep them for future use)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {deleted_reviews} reviews and {deleted_results} review results",
            "deleted_reviews": deleted_reviews,
            "deleted_results": deleted_results,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing reviews: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error clearing reviews: {str(e)}")

