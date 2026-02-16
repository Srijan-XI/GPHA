"""
Code churn analyzer.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List
from collections import defaultdict
from ..github_client import GitHubClient
from ..models import CodeChurnMetrics


class CodeChurnAnalyzer:
    """Analyzes code churn patterns."""
    
    def __init__(self, client: GitHubClient):
        """
        Initialize analyzer.
        
        Args:
            client: GitHub API client instance.
        """
        self.client = client
    
    def analyze(self, owner: str, repo: str, days: int = 90) -> CodeChurnMetrics:
        """
        Analyze code churn over specified period.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            days: Number of days to analyze (default: 90).
            
        Returns:
            CodeChurnMetrics with calculated scores.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get commits in the period
        commits = self.client.get_commits(owner, repo, since=since)
        
        # Track file-level changes
        file_changes = defaultdict(lambda: {"additions": 0, "deletions": 0, "commits": 0})
        total_additions = 0
        total_deletions = 0
        total_files = set()
        
        for commit in commits:
            # Get commit details to see file changes
            # Note: This would require additional API calls per commit
            # For now, we'll use the commit stats if available
            if "stats" in commit:
                stats = commit["stats"]
                total_additions += stats.get("additions", 0)
                total_deletions += stats.get("deletions", 0)
            
            # Get files from commit (would need detailed commit API call)
            # This is a simplified version
            if "files" in commit:
                for file in commit["files"]:
                    filename = file["filename"]
                    total_files.add(filename)
                    file_changes[filename]["additions"] += file.get("additions", 0)
                    file_changes[filename]["deletions"] += file.get("deletions", 0)
                    file_changes[filename]["commits"] += 1
        
        # Calculate churn rate (this is simplified - ideally we'd know total LOC)
        # Using total changes as a proxy
        total_changes = total_additions + total_deletions
        churn_rate = total_changes / max(len(commits), 1)
        
        # Identify hotspot files (files changed most frequently)
        hotspots = sorted(
            [
                {
                    "file": file,
                    "changes": data["additions"] + data["deletions"],
                    "commits": data["commits"]
                }
                for file, data in file_changes.items()
            ],
            key=lambda x: x["commits"],
            reverse=True
        )[:10]  # Top 10 hotspots
        
        # Files with high churn (changed in >20% of commits)
        high_churn_threshold = len(commits) * 0.2
        high_churn_files = [
            file for file, data in file_changes.items() 
            if data["commits"] > high_churn_threshold
        ]
        
        avg_changes_per_commit = total_changes / len(commits) if commits else 0
        
        metrics = CodeChurnMetrics(
            total_files_changed=len(total_files),
            total_additions=total_additions,
            total_deletions=total_deletions,
            churn_rate=round(churn_rate, 2),
            files_with_high_churn=high_churn_files,
            avg_changes_per_commit=round(avg_changes_per_commit, 2),
            hotspot_files=hotspots,
        )
        
        metrics.score = self._calculate_score(metrics, len(commits))
        
        return metrics
    
    def _calculate_score(self, metrics: CodeChurnMetrics, commit_count: int) -> float:
        """
        Calculate code quality score based on churn.
        
        Moderate churn is healthy, excessive churn may indicate issues.
        """
        score = 100.0
        
        if commit_count == 0:
            return 100.0
        
        # Penalize excessive churn (many changes per commit)
        # Healthy range: 50-200 lines per commit
        if metrics.avg_changes_per_commit > 500:
            score -= 20
        elif metrics.avg_changes_per_commit > 300:
            score -= 10
        
        # Penalize too many hotspot files (indicates lack of distribution)
        hotspot_penalty = min(len(metrics.files_with_high_churn) * 5, 30)
        score -= hotspot_penalty
        
        # Penalize very high deletion-to-addition ratio (could indicate instability)
        if metrics.total_additions > 0:
            deletion_ratio = metrics.total_deletions / metrics.total_additions
            if deletion_ratio > 0.8:  # More deletions than additions
                score -= 15
        
        return max(round(score, 2), 0.0)
