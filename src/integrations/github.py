"""GitHub API integration."""
from github import Github
from typing import Optional, List, Dict
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import settings

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """GitHub API integration for fetching code."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub integration.

        Args:
            token: GitHub personal access token
        """
        self.token = token or settings.github_token
        if self.token:
            self.github = Github(self.token)
        else:
            self.github = None
            logger.warning("GitHub token not provided, GitHub integration disabled")

    def get_repository(self, repo_url: str):
        """Get repository object from URL.

        Args:
            repo_url: Repository URL (e.g., 'owner/repo' or full URL)

        Returns:
            Repository object
        """
        if not self.github:
            raise ValueError("GitHub token not configured")

        # Extract owner/repo from URL
        if "github.com" in repo_url:
            parts = repo_url.replace("https://github.com/", "").replace("http://github.com/", "").split("/")
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace(".git", "")
                repo_path = f"{owner}/{repo}"
            else:
                raise ValueError(f"Invalid GitHub URL: {repo_url}")
        else:
            repo_path = repo_url

        return self.github.get_repo(repo_path)

    def get_file_content(self, repo_url: str, file_path: str, ref: Optional[str] = None) -> str:
        """Get file content from repository.

        Args:
            repo_url: Repository URL
            file_path: Path to file in repository
            ref: Git reference (branch, commit SHA, etc.)

        Returns:
            File content as string
        """
        if not self.github:
            raise ValueError("GitHub token not configured. Please set GITHUB_TOKEN in .env file.")
        
        repo = self.get_repository(repo_url)
        try:
            # PyGithub doesn't accept ref=None, only pass ref if it's provided
            if ref:
                file_content = repo.get_contents(file_path, ref=ref)
            else:
                file_content = repo.get_contents(file_path)
            
            # Handle case where get_contents returns a list (shouldn't happen for files, but handle it)
            if isinstance(file_content, list):
                if len(file_content) == 0:
                    raise ValueError(f"File '{file_path}' not found in repository.")
                # If it's a list, take the first item (shouldn't happen for files)
                file_content = file_content[0]
            
            if file_content is None:
                raise ValueError(f"File content is None for {file_path}")
            
            # Try to get content - handle both decoded_content and content attributes
            try:
                # Most common case: decoded_content exists
                if hasattr(file_content, 'decoded_content') and file_content.decoded_content:
                    content = file_content.decoded_content.decode("utf-8")
                # Fallback: use content attribute (base64 encoded)
                elif hasattr(file_content, 'content') and file_content.content:
                    import base64
                    content = base64.b64decode(file_content.content).decode("utf-8")
                else:
                    raise ValueError(f"Could not extract content from file '{file_path}'. File may be empty or binary.")
                
                if not content or not content.strip():
                    raise ValueError(f"File '{file_path}' is empty.")
                
                return content
                
            except UnicodeDecodeError:
                raise ValueError(f"File '{file_path}' appears to be a binary file. Only text files (Python, etc.) are supported.")
                
        except ValueError:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "Not Found" in error_msg:
                raise ValueError(
                    f"File '{file_path}' not found in repository '{repo_url}'. "
                    f"Please check if the file path is correct. "
                    f"File path should be relative to repository root (e.g., 'README.md', not '/README.md')."
                )
            elif "403" in error_msg or "Forbidden" in error_msg:
                raise ValueError(
                    f"Access forbidden to repository. Please check your GitHub token permissions."
                )
            else:
                logger.error(f"Error fetching file {file_path} from {repo_url}: {error_msg}", exc_info=True)
                raise ValueError(f"Error fetching file '{file_path}': {error_msg}")

    def get_pull_request_files(self, repo_url: str, pr_number: int) -> List[Dict[str, str]]:
        """Get files changed in a pull request.

        Args:
            repo_url: Repository URL
            pr_number: Pull request number

        Returns:
            List of dictionaries with file info and content
        """
        repo = self.get_repository(repo_url)
        pr = repo.get_pull(pr_number)
        files = []

        for file in pr.get_files():
            if file.filename.endswith(".py"):  # Only Python files
                try:
                    content = self.get_file_content(repo_url, file.filename, pr.head.sha)
                    files.append(
                        {
                            "path": file.filename,
                            "content": content,
                            "status": file.status,
                            "additions": file.additions,
                            "deletions": file.deletions,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not fetch file {file.filename}: {str(e)}")

        return files

    def get_commit_files(self, repo_url: str, commit_sha: str) -> List[Dict[str, str]]:
        """Get files changed in a commit.

        Args:
            repo_url: Repository URL
            commit_sha: Commit SHA

        Returns:
            List of dictionaries with file info and content
        """
        repo = self.get_repository(repo_url)
        commit = repo.get_commit(commit_sha)
        files = []

        for file in commit.files:
            if file.filename.endswith(".py") and file.status != "removed":
                try:
                    content = self.get_file_content(repo_url, file.filename, commit_sha)
                    files.append(
                        {
                            "path": file.filename,
                            "content": content,
                            "status": file.status,
                            "additions": file.additions,
                            "deletions": file.deletions,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not fetch file {file.filename}: {str(e)}")

        return files

    def get_all_python_files(self, repo_url: str, ref: Optional[str] = None) -> List[Dict[str, str]]:
        """Get all Python files from repository.

        Args:
            repo_url: Repository URL
            ref: Git reference (branch, commit SHA, etc.)

        Returns:
            List of dictionaries with file path and content
        """
        if not self.github:
            raise ValueError("GitHub token not configured. Please set GITHUB_TOKEN in .env file.")
        
        repo = self.get_repository(repo_url)
        files = []
        
        def get_files_recursive(path: str = "", ref: Optional[str] = None):
            """Recursively get all Python files from repository."""
            try:
                if ref:
                    contents = repo.get_contents(path, ref=ref)
                else:
                    contents = repo.get_contents(path)
                
                # Handle both single file and list of files
                if not isinstance(contents, list):
                    contents = [contents]
                
                for item in contents:
                    if item.type == "file" and item.name.endswith(".py"):
                        try:
                            if ref:
                                content = self.get_file_content(repo_url, item.path, ref)
                            else:
                                content = self.get_file_content(repo_url, item.path)
                            
                            files.append({
                                "path": item.path,
                                "content": content,
                                "size": item.size,
                            })
                            logger.info(f"Found Python file: {item.path}")
                        except Exception as e:
                            logger.warning(f"Could not fetch file {item.path}: {str(e)}")
                    elif item.type == "dir":
                        # Recursively search in subdirectories
                        # Skip common directories that don't contain source code
                        skip_dirs = [".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", ".vs", ".idea"]
                        if item.name not in skip_dirs and not item.name.startswith("."):
                            try:
                                get_files_recursive(item.path, ref)
                            except Exception as e:
                                logger.warning(f"Could not access directory {item.path}: {str(e)}")
            except Exception as e:
                logger.warning(f"Error accessing path {path}: {str(e)}")
        
        # Start recursive search from root
        get_files_recursive("", ref)
        
        logger.info(f"Found {len(files)} Python files in repository")
        return files

    def get_python_files_in_directory(self, repo_url: str, directory_path: str, ref: Optional[str] = None) -> List[Dict[str, str]]:
        """Get all Python files from a specific directory in repository.

        Args:
            repo_url: Repository URL
            directory_path: Directory path (e.g., 'scripts', 'src/utils')
            ref: Git reference (branch, commit SHA, etc.)

        Returns:
            List of dictionaries with file path and content
        """
        if not self.github:
            raise ValueError("GitHub token not configured. Please set GITHUB_TOKEN in .env file.")
        
        repo = self.get_repository(repo_url)
        files = []
        
        try:
            # Get contents of the directory
            if ref:
                contents = repo.get_contents(directory_path, ref=ref)
            else:
                contents = repo.get_contents(directory_path)
            
            # Handle both single file and list of files
            if not isinstance(contents, list):
                contents = [contents]
            
            for item in contents:
                if item.type == "file" and item.name.endswith(".py"):
                    try:
                        if ref:
                            content = self.get_file_content(repo_url, item.path, ref)
                        else:
                            content = self.get_file_content(repo_url, item.path)
                        
                        files.append({
                            "path": item.path,
                            "content": content,
                            "size": item.size,
                        })
                        logger.info(f"Found Python file: {item.path}")
                    except Exception as e:
                        logger.warning(f"Could not fetch file {item.path}: {str(e)}")
                elif item.type == "dir":
                    # Recursively search in subdirectories
                    try:
                        subdir_files = self.get_python_files_in_directory(repo_url, item.path, ref)
                        files.extend(subdir_files)
                    except Exception as e:
                        logger.warning(f"Could not access subdirectory {item.path}: {str(e)}")
        
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "Not Found" in error_msg:
                raise ValueError(
                    f"Directory '{directory_path}' not found in repository '{repo_url}'. "
                    f"Please check if the directory path is correct."
                )
            else:
                logger.error(f"Error accessing directory {directory_path} from {repo_url}: {error_msg}", exc_info=True)
                raise ValueError(f"Error accessing directory '{directory_path}': {error_msg}")
        
        logger.info(f"Found {len(files)} Python files in directory '{directory_path}'")
        return files

