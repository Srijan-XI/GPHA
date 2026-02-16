"""
Issue stagnation detector.
"""

from datetime import datetime, timedelta
from typing import List
from statistics import median
from ..github_client import GitHubClient
from ..models import IssueStagnationMetrics


class IssueStagnationAnalyzer:
    """Detects and analyzes stagnant issues."""
    
    def __init__(self, client: GitHubClient):
        """
        Initialize analyzer.
        
        Args:
            client: GitHub API client instance.
        """
        self.client = client
    
    def analyze(self, owner: str, repo: str) -> IssueStagnationMetrics:
        """
        Analyze issue stagnation patterns.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            
        Returns:
            IssueStagnationMetrics with calculated scores.
        """
        now = datetime.now()
        
        # Get all issues
        all_issues = self.client.get_issues(owner, repo, state="all")
        
        # Separate open and closed issues
        open_issues = [issue for issue in all_issues if issue["state"] == "open"]
        closed_issues = [issue for issue in all_issues if issue["state"] == "closed"]
        
        # Calculate stagnation periods
        stagnant_30 = []
        stagnant_90 = []
        stagnant_180 = []
        
        for issue in open_issues:
            updated_at = datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00"))
            days_since_update = (now - updated_at).days
            
            if days_since_update >= 180:
                stagnant_180.append(issue["number"])
                stagnant_90.append(issue["number"])
                stagnant_30.append(issue["number"])
            elif days_since_update >= 90:
                stagnant_90.append(issue["number"])
                stagnant_30.append(issue["number"])
            elif days_since_update >= 30:
                stagnant_30.append(issue["number"])
        
        # Calculate average time to close
        close_times = []
        for issue in closed_issues[:100]:  # Sample recent closed issues
            if issue.get("closed_at"):
                created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
                closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
                close_times.append((closed - created).days)
        
        avg_close_time = sum(close_times) / len(close_times) if close_times else 0
        
        # Calculate median age of open issues
        open_ages = []
        for issue in open_issues:
            created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            age_days = (now - created).days
            open_ages.append(age_days)
        
        median_age = median(open_ages) if open_ages else 0
        
        metrics = IssueStagnationMetrics(
            total_open_issues=len(open_issues),
            stagnant_issues_30_days=len(stagnant_30),
            stagnant_issues_90_days=len(stagnant_90),
            stagnant_issues_180_days=len(stagnant_180),
            avg_time_to_close_days=round(avg_close_time, 2),
            median_issue_age_days=round(median_age, 2),
            stagnant_issue_numbers=stagnant_90,  # Issues stagnant for 90+ days
        )
        
        metrics.score = self._calculate_score(metrics)
        
        return metrics
    
    def _calculate_score(self, metrics: IssueStagnationMetrics) -> float:
        """
        Calculate issue health score.
        
        Higher score = healthier issue management
        Lower stagnation = better score
        """
        score = 100.0
        
        if metrics.total_open_issues == 0:
            return 100.0
        
        # Penalize for stagnant issues
        stagnation_30_rate = metrics.stagnant_issues_30_days / metrics.total_open_issues
        stagnation_90_rate = metrics.stagnant_issues_90_days / metrics.total_open_issues
        stagnation_180_rate = metrics.stagnant_issues_180_days / metrics.total_open_issues
        
        # Heavy penalties for long-term stagnation
        score -= stagnation_30_rate * 20  # Max -20 points
        score -= stagnation_90_rate * 30  # Max -30 points
        score -= stagnation_180_rate * 40  # Max -40 points
        
        # Penalize for slow close times
        if metrics.avg_time_to_close_days > 30:
            score -= min((metrics.avg_time_to_close_days - 30) / 10, 10)
        
        return max(round(score, 2), 0.0)
