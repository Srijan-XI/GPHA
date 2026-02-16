"""
Tests for data models.
"""

import pytest
from datetime import datetime

from gpha.models import (
    HealthScore,
    ActivityMetrics,
    IssueStagnationMetrics,
    CodeChurnMetrics,
    ContributorMetrics,
    AnalysisReport,
)


class TestHealthScore:
    """Tests for HealthScore model."""
    
    def test_creation(self):
        """Test creating a HealthScore."""
        score = HealthScore(
            overall=85.5,
            activity=90.0,
            issue_health=80.0,
            code_quality=85.0,
            contributor_health=87.0
        )
        assert score.overall == 85.5
        assert score.activity == 90.0
        assert isinstance(score.timestamp, datetime)
    
    def test_to_dict(self):
        """Test converting HealthScore to dict."""
        score = HealthScore(
            overall=85.5,
            activity=90.0,
            issue_health=80.0,
            code_quality=85.0,
            contributor_health=87.0
        )
        data = score.to_dict()
        assert data["overall"] == 85.5
        assert data["activity"] == 90.0
        assert "timestamp" in data


class TestActivityMetrics:
    """Tests for ActivityMetrics model."""
    
    def test_creation(self):
        """Test creating ActivityMetrics."""
        metrics = ActivityMetrics(
            commits_last_30_days=50,
            commits_last_90_days=150,
            prs_opened_last_30_days=10,
            prs_merged_last_30_days=8,
            issues_opened_last_30_days=5,
            issues_closed_last_30_days=7,
            active_contributors_last_30_days=3,
            score=85.0
        )
        assert metrics.commits_last_30_days == 50
        assert metrics.score == 85.0


class TestAnalysisReport:
    """Tests for AnalysisReport model."""
    
    def test_creation_and_to_dict(self):
        """Test creating and converting AnalysisReport."""
        health_score = HealthScore(
            overall=85.0,
            activity=90.0,
            issue_health=80.0,
            code_quality=85.0,
            contributor_health=87.0
        )
        
        activity = ActivityMetrics(
            commits_last_30_days=50,
            commits_last_90_days=150,
            prs_opened_last_30_days=10,
            prs_merged_last_30_days=8,
            issues_opened_last_30_days=5,
            issues_closed_last_30_days=7,
            active_contributors_last_30_days=3,
            score=90.0
        )
        
        issue_metrics = IssueStagnationMetrics(
            total_open_issues=10,
            stagnant_issues_30_days=2,
            stagnant_issues_90_days=1,
            stagnant_issues_180_days=0,
            avg_time_to_close_days=5.0,
            median_issue_age_days=10.0,
            score=80.0
        )
        
        churn_metrics = CodeChurnMetrics(
            total_files_changed=100,
            total_additions=1000,
            total_deletions=500,
            churn_rate=0.15,
            score=85.0
        )
        
        contributor_metrics = ContributorMetrics(
            total_contributors=20,
            active_contributors_30_days=5,
            active_contributors_90_days=10,
            new_contributors_30_days=2,
            core_contributors=3,
            bus_factor=2,
            score=87.0
        )
        
        report = AnalysisReport(
            repository="owner/repo",
            health_score=health_score,
            activity_metrics=activity,
            issue_metrics=issue_metrics,
            churn_metrics=churn_metrics,
            contributor_metrics=contributor_metrics
        )
        
        assert report.repository == "owner/repo"
        
        data = report.to_dict()
        assert data["repository"] == "owner/repo"
        assert "health_score" in data
        assert "activity_metrics" in data
        assert isinstance(data["analyzed_at"], str)
