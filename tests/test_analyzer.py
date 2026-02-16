"""
Tests for main HealthAnalyzer orchestrator.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from gpha.analyzer import HealthAnalyzer
from gpha.config import Config
from gpha.models import (
    ActivityMetrics,
    IssueStagnationMetrics,
    CodeChurnMetrics,
    ContributorMetrics,
)


class TestHealthAnalyzer:
    """Tests for HealthAnalyzer."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "github.token": "test_token",
            "analysis.churn_period_days": 90,
            "scoring.weights": {
                "activity": 0.30,
                "issue_health": 0.25,
                "code_quality": 0.25,
                "contributor_health": 0.20
            }
        }.get(key, default)
        return config
    
    @patch("gpha.analyzer.GitHubClient")
    @patch("gpha.analyzer.RepoActivityAnalyzer")
    @patch("gpha.analyzer.IssueStagnationAnalyzer")
    @patch("gpha.analyzer.CodeChurnAnalyzer")
    @patch("gpha.analyzer.ContributorPatternsAnalyzer")
    def test_analyze_repository(
        self, 
        mock_contrib, 
        mock_churn, 
        mock_issue, 
        mock_activity, 
        mock_client,
        mock_config
    ):
        """Test complete repository analysis."""
        # Setup mocks
        mock_activity_instance = Mock()
        mock_activity_instance.analyze.return_value = ActivityMetrics(
            commits_last_30_days=50,
            commits_last_90_days=150,
            prs_opened_last_30_days=10,
            prs_merged_last_30_days=8,
            issues_opened_last_30_days=5,
            issues_closed_last_30_days=7,
            active_contributors_last_30_days=3,
            score=90.0
        )
        mock_activity.return_value = mock_activity_instance
        
        mock_issue_instance = Mock()
        mock_issue_instance.analyze.return_value = IssueStagnationMetrics(
            total_open_issues=10,
            stagnant_issues_30_days=2,
            stagnant_issues_90_days=1,
            stagnant_issues_180_days=0,
            avg_time_to_close_days=5.0,
            median_issue_age_days=10.0,
            score=80.0
        )
        mock_issue.return_value = mock_issue_instance
        
        mock_churn_instance = Mock()
        mock_churn_instance.analyze.return_value = CodeChurnMetrics(
            total_files_changed=100,
            total_additions=1000,
            total_deletions=500,
            churn_rate=0.15,
            score=85.0
        )
        mock_churn.return_value = mock_churn_instance
        
        mock_contrib_instance = Mock()
        mock_contrib_instance.analyze.return_value = ContributorMetrics(
            total_contributors=20,
            active_contributors_30_days=5,
            active_contributors_90_days=10,
            new_contributors_30_days=2,
            core_contributors=3,
            bus_factor=2,
            score=87.0
        )
        mock_contrib.return_value = mock_contrib_instance
        
        # Create analyzer and run
        analyzer = HealthAnalyzer(config=mock_config)
        report = analyzer.analyze_repository("owner", "repo")
        
        # Verify results
        assert report.repository == "owner/repo"
        assert report.health_score.overall > 0
        assert report.health_score.activity == 90.0
        assert report.health_score.issue_health == 80.0
        assert report.health_score.code_quality == 85.0
        assert report.health_score.contributor_health == 87.0
        
        # Verify all analyzers were called
        mock_activity_instance.analyze.assert_called_once_with("owner", "repo")
        mock_issue_instance.analyze.assert_called_once_with("owner", "repo")
        mock_churn_instance.analyze.assert_called_once()
        mock_contrib_instance.analyze.assert_called_once_with("owner", "repo")
    
    def test_calculate_overall_health(self, mock_config):
        """Test health score calculation."""
        with patch("gpha.analyzer.GitHubClient"):
            analyzer = HealthAnalyzer(config=mock_config)
            
            score = analyzer._calculate_overall_health(
                activity_score=90.0,
                issue_score=80.0,
                churn_score=85.0,
                contributor_score=87.0
            )
            
            assert score.overall > 0
            assert score.overall <= 100
            assert score.activity == 90.0
            assert score.issue_health == 80.0
