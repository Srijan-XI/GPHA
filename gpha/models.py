"""
Data models for GPHA.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class HealthScore:
    """Overall health score for a repository."""
    
    overall: float
    activity: float
    issue_health: float
    code_quality: float
    contributor_health: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "overall": self.overall,
            "activity": self.activity,
            "issue_health": self.issue_health,
            "code_quality": self.code_quality,
            "contributor_health": self.contributor_health,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ActivityMetrics:
    """Repository activity metrics."""
    
    commits_last_30_days: int
    commits_last_90_days: int
    prs_opened_last_30_days: int
    prs_merged_last_30_days: int
    issues_opened_last_30_days: int
    issues_closed_last_30_days: int
    active_contributors_last_30_days: int
    score: float = 0.0


@dataclass
class IssueStagnationMetrics:
    """Issue stagnation metrics."""
    
    total_open_issues: int
    stagnant_issues_30_days: int
    stagnant_issues_90_days: int
    stagnant_issues_180_days: int
    avg_time_to_close_days: float
    median_issue_age_days: float
    score: float = 0.0
    stagnant_issue_numbers: List[int] = field(default_factory=list)


@dataclass
class CodeChurnMetrics:
    """Code churn analysis metrics."""
    
    total_files_changed: int
    total_additions: int
    total_deletions: int
    churn_rate: float  # (additions + deletions) / total_lines
    files_with_high_churn: List[str] = field(default_factory=list)
    avg_changes_per_commit: float = 0.0
    hotspot_files: List[Dict[str, int]] = field(default_factory=list)
    score: float = 0.0


@dataclass
class ContributorMetrics:
    """Contributor pattern metrics."""
    
    total_contributors: int
    active_contributors_30_days: int
    active_contributors_90_days: int
    new_contributors_30_days: int
    core_contributors: int  # Contributors with >10 commits
    contribution_distribution: Dict[str, int] = field(default_factory=dict)
    bus_factor: int = 1  # Minimum contributors for 50% of commits
    score: float = 0.0


@dataclass
class AnalysisReport:
    """Complete analysis report for a repository."""
    
    repository: str
    health_score: HealthScore
    activity_metrics: ActivityMetrics
    issue_metrics: IssueStagnationMetrics
    churn_metrics: CodeChurnMetrics
    contributor_metrics: ContributorMetrics
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "repository": self.repository,
            "health_score": self.health_score.to_dict(),
            "activity_metrics": self.activity_metrics.__dict__,
            "issue_metrics": self.issue_metrics.__dict__,
            "churn_metrics": self.churn_metrics.__dict__,
            "contributor_metrics": self.contributor_metrics.__dict__,
            "analyzed_at": self.analyzed_at.isoformat(),
        }
