"""
Contributor patterns analyzer.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
from ..github_client import GitHubClient
from ..models import ContributorMetrics


class ContributorPatternsAnalyzer:
    """Analyzes contributor patterns and health."""
    
    def __init__(self, client: GitHubClient):
        """
        Initialize analyzer.
        
        Args:
            client: GitHub API client instance.
        """
        self.client = client
    
    def analyze(self, owner: str, repo: str) -> ContributorMetrics:
        """
        Analyze contributor patterns.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            
        Returns:
            ContributorMetrics with calculated scores.
        """
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)
        
        # Get all contributors
        all_contributors = self.client.get_contributors(owner, repo)
        total_contributors = len(all_contributors)
        
        # Get recent commits to analyze activity
        commits_30 = self.client.get_commits(owner, repo, since=thirty_days_ago)
        commits_90 = self.client.get_commits(owner, repo, since=ninety_days_ago)
        
        # Count contributions per author
        contributions_30 = defaultdict(int)
        contributions_90 = defaultdict(int)
        contributions_all = defaultdict(int)
        
        # Track contributors in last 30 days
        for commit in commits_30:
            author = commit.get("commit", {}).get("author", {}).get("email", "unknown")
            contributions_30[author] += 1
        
        # Track contributors in last 90 days
        for commit in commits_90:
            author = commit.get("commit", {}).get("author", {}).get("email", "unknown")
            contributions_90[author] += 1
        
        # Get all-time contributions from contributors list
        for contributor in all_contributors:
            contributions_all[contributor["login"]] = contributor.get("contributions", 0)
        
        active_30 = len(contributions_30)
        active_90 = len(contributions_90)
        
        # Identify new contributors (active in last 30 days but not in 30-90 day window)
        old_contributors = set(contributions_90.keys()) - set(contributions_30.keys())
        new_contributors = active_30 - len(old_contributors)
        new_contributors = max(0, new_contributors)  # Ensure non-negative
        
        # Identify core contributors (>10 commits all-time)
        core_contributors = len([
            contrib for contrib in all_contributors 
            if contrib.get("contributions", 0) >= 10
        ])
        
        # Calculate bus factor (simplified)
        # Number of contributors needed to account for 50% of commits
        sorted_contribs = sorted(contributions_all.values(), reverse=True)
        total_commits = sum(sorted_contribs)
        cumulative = 0
        bus_factor = 0
        target = total_commits * 0.5
        
        for contrib_count in sorted_contribs:
            cumulative += contrib_count
            bus_factor += 1
            if cumulative >= target:
                break
        
        # Build contribution distribution (top 10 contributors)
        top_contributors = sorted(
            contributions_all.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        contribution_dist = {name: count for name, count in top_contributors}
        
        metrics = ContributorMetrics(
            total_contributors=total_contributors,
            active_contributors_30_days=active_30,
            active_contributors_90_days=active_90,
            new_contributors_30_days=new_contributors,
            core_contributors=core_contributors,
            contribution_distribution=contribution_dist,
            bus_factor=bus_factor,
        )
        
        metrics.score = self._calculate_score(metrics)
        
        return metrics
    
    def _calculate_score(self, metrics: ContributorMetrics) -> float:
        """
        Calculate contributor health score.
        
        Healthy projects have:
        - Multiple active contributors
        - Good bus factor (not dependent on 1-2 people)
        - Growing contributor base
        - Balance in contribution distribution
        """
        score = 0.0
        
        # Active contributors (40 points max)
        # 10+ active in last 30 days = full points
        active_score = min(metrics.active_contributors_30_days / 10 * 40, 40)
        score += active_score
        
        # Bus factor (30 points max)
        # Bus factor >= 5 = full points, 1-2 is risky
        if metrics.bus_factor >= 5:
            bus_score = 30
        elif metrics.bus_factor >= 3:
            bus_score = 20
        elif metrics.bus_factor >= 2:
            bus_score = 10
        else:
            bus_score = 5  # High risk
        score += bus_score
        
        # Core contributors (15 points max)
        # 5+ core contributors = full points
        core_score = min(metrics.core_contributors / 5 * 15, 15)
        score += core_score
        
        # New contributor growth (15 points max)
        # 3+ new contributors/month = full points
        new_contrib_score = min(metrics.new_contributors_30_days / 3 * 15, 15)
        score += new_contrib_score
        
        return round(score, 2)
