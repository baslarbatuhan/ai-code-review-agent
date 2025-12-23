"""Streamlit dashboard for code review agent."""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI-Powered Code Review Agent")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["New Review", "Review History", "Analytics"])

if page == "New Review":
    st.header("Create New Code Review")

    with st.form("review_form"):
        repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/owner/repo",
            help="Enter GitHub repository URL",
        )

        col1, col2 = st.columns(2)

        with col1:
            file_path = st.text_input(
                "File Path (optional)",
                placeholder="src/main.py",
                help="Specific file to review",
            )
            commit_sha = st.text_input(
                "Commit SHA (optional)",
                placeholder="abc123...",
                help="Specific commit to review",
            )

        with col2:
            pr_id = st.number_input(
                "Pull Request ID (optional)",
                min_value=0,
                value=0,
                help="Pull request number (set to 0 or leave empty if using file_path)",
            )
            scan_entire_repo = st.checkbox(
                "🔍 Scan Entire Repository",
                value=False,
                help="Scan all Python files in the repository (ignores file_path if enabled)",
            )
            agent_types = st.multiselect(
                "Agent Types (leave empty for all)",
                ["quality", "security", "performance", "documentation"],
                help="Select specific agents to run",
            )

        submitted = st.form_submit_button("Start Review", type="primary")

        if submitted:
            if not repo_url:
                st.error("Please provide a repository URL")
            else:
                # Determine if this is a directory scan or repository scan
                is_directory_scan = file_path and not file_path.endswith('.py') and not scan_entire_repo
                is_repository_scan = scan_entire_repo
                
                # Show appropriate message and set timeout
                if is_repository_scan:
                    status_message = "Scanning entire repository (this may take up to 30 minutes)..."
                    timeout = 1800  # 30 minutes (1800 seconds)
                elif is_directory_scan:
                    status_message = "Scanning directory (this may take up to 10 minutes)..."
                    timeout = 600  # 10 minutes (600 seconds)
                else:
                    status_message = "Reviewing code..."
                    timeout = 60  # 1 minute (60 seconds)
                
                with st.spinner(status_message):
                    try:
                        payload = {
                            "repository_url": repo_url,
                        }

                        # Scan entire repo takes priority
                        if scan_entire_repo:
                            payload["scan_entire_repo"] = True
                        else:
                            if file_path:
                                payload["file_path"] = file_path
                        
                        if commit_sha:
                            payload["commit_sha"] = commit_sha
                        # Only send PR ID if it's greater than 0 (0 means not used)
                        if pr_id and pr_id > 0:
                            payload["pull_request_id"] = int(pr_id)
                        if agent_types:
                            payload["agent_types"] = agent_types

                        # Timeout based on scan type
                        response = requests.post(f"{API_URL}/reviews", json=payload, timeout=timeout)

                        if response.status_code == 200:
                            review_data = response.json()
                            st.success("Review completed!")
                            st.session_state["last_review"] = review_data
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")

                    except Exception as e:
                        st.error(f"Error creating review: {str(e)}")

    # Display last review if available
    if "last_review" in st.session_state:
        st.markdown("---")
        st.header("Review Results")
        review = st.session_state["last_review"]

        st.metric("Total Issues", review["total_issues"])
        st.metric("File", review["file_path"])

        # Severity filter
        st.markdown("### 🔍 Filter by Severity")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            show_critical = st.checkbox("🔴 Critical", value=True, key="filter_critical")
        with col2:
            show_high = st.checkbox("🟠 High", value=True, key="filter_high")
        with col3:
            show_medium = st.checkbox("🟡 Medium", value=True, key="filter_medium")
        with col4:
            show_low = st.checkbox("🟢 Low", value=True, key="filter_low")
        with col5:
            show_info = st.checkbox("🔵 Info", value=True, key="filter_info")
        
        # Create set of selected severities
        selected_severities = set()
        if show_critical:
            selected_severities.add("critical")
        if show_high:
            selected_severities.add("high")
        if show_medium:
            selected_severities.add("medium")
        if show_low:
            selected_severities.add("low")
        if show_info:
            selected_severities.add("info")
        
        st.markdown("---")

        # Display results by agent
        for agent_result in review["results"]:
            # Count filtered issues for this agent
            filtered_count = sum(
                1 for issue in agent_result["issues"]
                if issue.get('severity', '').lower() in selected_severities
            )
            total_count = len(agent_result["issues"])
            
            # Show expander with filtered count
            if filtered_count == 0:
                expander_label = f"🔹 {agent_result['agent_type'].upper()} Agent ({total_count} total, 0 filtered)"
            else:
                expander_label = f"🔹 {agent_result['agent_type'].upper()} Agent ({filtered_count}/{total_count} issues)"
            
            with st.expander(expander_label):
                if agent_result["success"]:
                    if agent_result["issues"]:
                        # Filter issues by selected severities
                        filtered_issues = [
                            issue for issue in agent_result["issues"]
                            if issue.get('severity', '').lower() in selected_severities
                        ]
                        
                        if not filtered_issues:
                            st.info(f"No issues found with selected severity levels for {agent_result['agent_type'].upper()} Agent.")
                            continue
                        
                        # Group issues by file for better organization
                        issues_by_file = {}
                        for issue in filtered_issues:
                            # Extract file path from message or metadata
                            file_path = None
                            issue_message = issue.get('message', '')
                            
                            # Priority 1: Check metadata first (most reliable)
                            if issue.get('metadata') and isinstance(issue['metadata'], dict):
                                file_path = issue['metadata'].get('file_path')
                            
                            # Priority 2: Check if message starts with [file_path] format
                            if not file_path and issue_message.startswith('[') and ']' in issue_message:
                                end_bracket = issue_message.index(']')
                                file_path = issue_message[1:end_bracket]
                                issue_message = issue_message[end_bracket + 2:].strip()  # Remove [file] and space
                            
                            # Clean up issue message if it still contains file path prefix
                            if issue_message.startswith('[') and ']' in issue_message:
                                end_bracket = issue_message.index(']')
                                # Only remove if we don't have file_path from metadata
                                if not file_path:
                                    file_path = issue_message[1:end_bracket]
                                issue_message = issue_message[end_bracket + 2:].strip()
                            
                            # Use file_path or default - ensure we have a valid file path
                            file_key = file_path if file_path and file_path != "unknown" else "Unknown File"
                            
                            if file_key not in issues_by_file:
                                issues_by_file[file_key] = []
                            
                            issues_by_file[file_key].append({
                                **issue,
                                'display_message': issue_message,
                                'file_path': file_path
                            })
                        
                        # Display issues grouped by file
                        for file_path_key, file_issues in issues_by_file.items():
                            # Always show file path header if we have file information
                            if file_path_key and file_path_key != "Unknown File":
                                st.markdown(f"#### 📁 **File:** `{file_path_key}` ({len(file_issues)} issues)")
                                st.markdown("")  # Empty line for spacing
                            
                            for issue in file_issues:
                                severity_color = {
                                    "critical": "🔴",
                                    "high": "🟠",
                                    "medium": "🟡",
                                    "low": "🟢",
                                    "info": "🔵",
                                }
                                icon = severity_color.get(issue["severity"], "⚪")
                                
                                # Display issue with file path prominently
                                if file_path_key and file_path_key != "Unknown File":
                                    st.markdown(
                                        f"""
                                        **{icon} {issue['severity'].upper()}** - `{issue['issue_type']}`
                                        - **📁 File:** `{file_path_key}`
                                        - **📍 Line {issue.get('line_number', 'N/A')}**: {issue['display_message']}
                                        - **💡 Suggestion**: {issue.get('suggestion', 'N/A')}
                                        """
                                    )
                                else:
                                    # Fallback if file path not found
                                    st.markdown(
                                        f"""
                                        **{icon} {issue['severity'].upper()}** - `{issue['issue_type']}`
                                        - **📍 Line {issue.get('line_number', 'N/A')}**: {issue.get('message', issue['display_message'])}
                                        - **💡 Suggestion**: {issue.get('suggestion', 'N/A')}
                                        """
                                    )
                                st.markdown("---")
                    else:
                        st.success("No issues found!")
                else:
                    st.error(f"Agent failed: {agent_result.get('error_message', 'Unknown error')}")

elif page == "Review History":
    st.header("Review History")

    # Clear history button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")  # Spacing
    with col2:
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_clear", False):
                # Actually clear
                try:
                    response = requests.delete(f"{API_URL}/reviews")
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result.get('message', 'History cleared successfully!')}")
                        st.session_state["confirm_clear"] = False
                        st.session_state.pop("last_review", None)  # Clear last review from session
                        st.rerun()
                    else:
                        st.error(f"Error clearing history: {response.text}")
                except Exception as e:
                    st.error(f"Error clearing history: {str(e)}")
            else:
                st.session_state["confirm_clear"] = True
                st.warning("⚠️ Click again to confirm clearing all review history. This action cannot be undone!")
                st.rerun()
    
    # Show confirmation message if needed
    if st.session_state.get("confirm_clear", False):
        st.warning("⚠️ Click 'Clear All History' again to confirm. This will delete all reviews and analytics data!")

    try:
        # Fetch reviews from API
        response = requests.get(f"{API_URL}/reviews?limit=50")
        
        if response.status_code == 200:
            reviews = response.json()
            
            if not reviews:
                st.info("No reviews found. Create your first review from the 'New Review' page!")
            else:
                st.metric("Total Reviews", len(reviews))
                st.markdown("---")
                
                # Display reviews
                for review in reviews:
                    with st.expander(
                        f"📋 Review #{review['review_id']} - {review['file_path']} "
                        f"({review['total_issues']} issues) - {review['status'].upper()}"
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Repository:**\n{review['repository_url']}")
                        with col2:
                            st.markdown(f"**File Path:**\n`{review['file_path']}`")
                        with col3:
                            st.markdown(f"**Status:**\n{review['status'].upper()}")
                        
                        st.markdown(f"**Created:** {review['created_at']}")
                        if review.get('completed_at'):
                            st.markdown(f"**Completed:** {review['completed_at']}")
                        
                        # Show summary by agent
                        if review.get('results'):
                            st.markdown("### Agent Results Summary")
                            for agent_result in review['results']:
                                st.markdown(
                                    f"- **{agent_result['agent_type'].upper()}**: "
                                    f"{len(agent_result['issues'])} issues"
                                )
                        
                        # View details button
                        if st.button(f"View Details", key=f"view_{review['review_id']}"):
                            st.session_state["selected_review_id"] = review['review_id']
                            st.session_state["last_review"] = review
                            st.rerun()
                        
                        st.markdown("---")
        else:
            st.error(f"Error loading reviews: {response.text}")

    except Exception as e:
        st.error(f"Error loading review history: {str(e)}")

elif page == "Analytics":
    st.header("Analytics & Metrics")

    try:
        # Fetch analytics from API
        response = requests.get(f"{API_URL}/analytics")
        
        if response.status_code == 200:
            analytics = response.json()
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Reviews", analytics.get("total_reviews", 0))
            with col2:
                st.metric("Total Issues", analytics.get("total_issues", 0))
            with col3:
                st.metric("Avg Issues/Review", f"{analytics.get('avg_issues_per_review', 0):.1f}")
            with col4:
                st.metric("Success Rate", f"{analytics.get('success_rate', 0):.1f}%")
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Issues by Severity")
                severity_stats = analytics.get("severity_stats", {})
                if severity_stats:
                    severity_df = pd.DataFrame({
                        "Severity": list(severity_stats.keys()),
                        "Count": list(severity_stats.values())
                    })
                    st.bar_chart(severity_df.set_index("Severity"))
                else:
                    st.info("No severity data available")
            
            with col2:
                st.subheader("Issues by Agent Type")
                agent_stats = analytics.get("agent_stats", {})
                if agent_stats:
                    agent_df = pd.DataFrame({
                        "Agent Type": list(agent_stats.keys()),
                        "Count": list(agent_stats.values())
                    })
                    st.bar_chart(agent_df.set_index("Agent Type"))
                else:
                    st.info("No agent data available")
            
            st.markdown("---")
            
            # Repository statistics
            st.subheader("Top Repositories")
            repo_stats = analytics.get("repo_stats", [])
            if repo_stats:
                repo_df = pd.DataFrame(repo_stats)
                st.dataframe(repo_df, use_container_width=True)
            else:
                st.info("No repository data available")
            
            st.markdown("---")
            
            # Additional stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Completed Reviews", analytics.get("completed_reviews", 0))
            with col2:
                st.metric("Recent Reviews (7 days)", analytics.get("recent_reviews", 0))
        else:
            st.error(f"Error loading analytics: {response.text}")

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

