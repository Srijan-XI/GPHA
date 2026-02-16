"""
Main analyzer orchestrator.
"""

from typing import Optional
from .github_client import GitHubClient
from .analyzers import (
    RepoActivityAnalyzer,
    IssueStagnationAnalyzer,
    CodeChurnAnalyzer,
    ContributorPatternsAnalyzer,
)
from .models import AnalysisReport, HealthScore
from .config import Config


class HealthAnalyzer:
    """Main orchestrator for repository health analysis."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize health analyzer.
        
        Args:
            config: Configuration instance. If None, uses default config.
        """
        self.config = config or Config()
        
        # Initialize GitHub client
        token = self.config.get("github.token")
        self.client = GitHubClient(token=token)
        
        # Initialize analyzers
        self.activity_analyzer = RepoActivityAnalyzer(self.client)
        self.issue_analyzer = IssueStagnationAnalyzer(self.client)
        self.churn_analyzer = CodeChurnAnalyzer(self.client)
        self.contributor_analyzer = ContributorPatternsAnalyzer(self.client)
    
    def analyze_repository(self, owner: str, repo: str) -> AnalysisReport:
        """
        Run complete health analysis on a repository.
        
        Args:
            owner: Repository owner.
            repo: Repository name.
            
        Returns:
            Complete AnalysisReport with all metrics and scores.
        """
        print(f"Analyzing {owner}/{repo}...")
        
        # Run all analyzers
        print("  - Analyzing repository activity...")
        activity_metrics = self.activity_analyzer.analyze(owner, repo)
        
        print("  - Detecting issue stagnation...")
        issue_metrics = self.issue_analyzer.analyze(owner, repo)
        
        print("  - Analyzing code churn...")
        churn_metrics = self.churn_analyzer.analyze(
            owner, repo,
            days=self.config.get("analysis.churn_period_days", 90)
        )
        
        print("  - Analyzing contributor patterns...")
        contributor_metrics = self.contributor_analyzer.analyze(owner, repo)
        
        # Calculate overall health score
        health_score = self._calculate_overall_health(
            activity_metrics.score,
            issue_metrics.score,
            churn_metrics.score,
            contributor_metrics.score,
        )
        
        # Create report
        report = AnalysisReport(
            repository=f"{owner}/{repo}",
            health_score=health_score,
            activity_metrics=activity_metrics,
            issue_metrics=issue_metrics,
            churn_metrics=churn_metrics,
            contributor_metrics=contributor_metrics,
        )
        
        print(f"\n✓ Analysis complete! Overall health score: {health_score.overall}/100")
        
        return report
    
    def _calculate_overall_health(
        self,
        activity_score: float,
        issue_score: float,
        churn_score: float,
        contributor_score: float,
    ) -> HealthScore:
        """
        Calculate weighted overall health score.
        
        Uses weights from configuration.
        """
        weights = self.config.get("scoring.weights", {})
        
        overall = (
            activity_score * weights.get("activity", 0.30) +
            issue_score * weights.get("issue_health", 0.25) +
            churn_score * weights.get("code_quality", 0.25) +
            contributor_score * weights.get("contributor_health", 0.20)
        )
        
        return HealthScore(
            overall=round(overall, 2),
            activity=activity_score,
            issue_health=issue_score,
            code_quality=churn_score,
            contributor_health=contributor_score,
        )
