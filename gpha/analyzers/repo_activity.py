"""
Repository activity analyzer.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from ..github_client import GitHubClient
from ..models import ActivityMetrics


class RepoActivityAnalyzer:
    """Analyzes repository activity metrics."""
    
    def __init__(self, client: GitHubClient):
        """
        Initialize analyzer.
        
        Args:
            client: GitHub API client instance.
        """
        self.client = client
    
    def analyze(self, owner: str, repo: str) -> ActivityMetrics:
        """
        Analyze repository activity.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            
        Returns:
            ActivityMetrics with calculated scores.
        """
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)
        
        # Get commits
        commits_30 = self.client.get_commits(owner, repo, since=thirty_days_ago)
        commits_90 = self.client.get_commits(owner, repo, since=ninety_days_ago)
        
        # Get pull requests
        all_prs = self.client.get_pull_requests(owner, repo, state="all")
        prs_opened_30 = len([
            pr for pr in all_prs 
            if datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")) >= thirty_days_ago
        ])
        prs_merged_30 = len([
            pr for pr in all_prs 
            if pr.get("merged_at") and 
            datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00")) >= thirty_days_ago
        ])
        
        # Get issues
        issues = self.client.get_issues(owner, repo, state="all", since=thirty_days_ago)
        issues_opened_30 = len([
            issue for issue in issues
            if datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00")) >= thirty_days_ago
        ])
        issues_closed_30 = len([
            issue for issue in issues
            if issue.get("closed_at") and
            datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00")) >= thirty_days_ago
        ])
        
        # Count active contributors (unique commit authors in last 30 days)
        active_contributors = len(set(
            commit["commit"]["author"]["email"] 
            for commit in commits_30 
            if commit.get("commit", {}).get("author", {}).get("email")
        ))
        
        metrics = ActivityMetrics(
            commits_last_30_days=len(commits_30),
            commits_last_90_days=len(commits_90),
            prs_opened_last_30_days=prs_opened_30,
            prs_merged_last_30_days=prs_merged_30,
            issues_opened_last_30_days=issues_opened_30,
            issues_closed_last_30_days=issues_closed_30,
            active_contributors_last_30_days=active_contributors,
        )
        
        # Calculate activity score (0-100)
        metrics.score = self._calculate_score(metrics)
        
        return metrics
    
    def _calculate_score(self, metrics: ActivityMetrics) -> float:
        """
        Calculate activity score based on metrics.
        
        Scoring factors:
        - Commit frequency (40 points)
        - PR activity (25 points)
        - Issue management (20 points)
        - Active contributors (15 points)
        """
        score = 0.0
        
        # Commit activity (40 points max)
        # 10+ commits/month = full points
        commit_score = min(metrics.commits_last_30_days / 10 * 40, 40)
        score += commit_score
        
        # PR activity (25 points max)
        # 5+ PRs opened and 80% merge rate = full points
        pr_opened_score = min(metrics.prs_opened_last_30_days / 5 * 15, 15)
        merge_rate = (metrics.prs_merged_last_30_days / metrics.prs_opened_last_30_days 
                      if metrics.prs_opened_last_30_days > 0 else 0)
        pr_merge_score = merge_rate * 10
        score += pr_opened_score + pr_merge_score
        
        # Issue management (20 points max)
        # High issue close rate = healthy
        if metrics.issues_opened_last_30_days > 0:
            close_rate = metrics.issues_closed_last_30_days / metrics.issues_opened_last_30_days
            issue_score = min(close_rate * 20, 20)
        else:
            issue_score = 15  # No new issues is also okay
        score += issue_score
        
        # Active contributors (15 points max)
        # 5+ active contributors = full points
        contributor_score = min(metrics.active_contributors_last_30_days / 5 * 15, 15)
        score += contributor_score
        
        return round(score, 2)
