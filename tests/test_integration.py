"""
Integration tests for GPHA.
"""

import pytest
import os
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from gpha import HealthAnalyzer
from gpha.config import Config
from gpha.github_client import GitHubClient


class TestIntegration:
    """Integration tests for full workflow."""
    
    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_integration_token"})
    @patch("gpha.github_client.requests.Session")
    def test_full_analysis_workflow(self, mock_session_class):
        """Test complete analysis workflow from start to finish."""
        # Setup comprehensive mock responses
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        now = datetime.now(timezone.utc)
        
        # Mock responses for various API calls
        def mock_get(url, params=None):
            response = Mock()
            response.raise_for_status = Mock()
            
            # Determine what endpoint is being called based on URL
            if "commits" in url:
                # Return commits on first page, empty on second
                if params and params.get("page", 1) == 1:
                    response.json.return_value = [
                        {
                            "sha": f"sha{i}",
                            "commit": {
                                "author": {
                                    "email": f"user{i % 3}@example.com",
                                    "date": now.isoformat()
                                }
                            },
                            "stats": {
                                "additions": 50,
                                "deletions": 20
                            },
                            "files": [
                                {
                                    "filename": f"file{i}.py",
                                    "additions": 50,
                                    "deletions": 20,
                                    "changes": 70
                                }
                            ]
                        }
                        for i in range(20)
                    ]
                else:
                    response.json.return_value = []
            elif "issues" in url:
                if params and params.get("page", 1) == 1:
                    response.json.return_value = [
                        {
                            "number": i,
                            "state": "open" if i % 2 == 0 else "closed",
                            "created_at": now.isoformat(),
                            "updated_at": now.isoformat(),
                            "closed_at": now.isoformat() if i % 2 == 1 else None
                        }
                        for i in range(10)
                    ]
                else:
                    response.json.return_value = []
            elif "pulls" in url:
                if params and params.get("page", 1) == 1:
                    response.json.return_value = [
                        {
                            "number": i,
                            "state": "open" if i % 3 == 0 else "closed",
                            "created_at": now.isoformat(),
                            "merged_at": now.isoformat() if i % 3 != 0 else None
                        }
                        for i in range(5)
                    ]
                else:
                    response.json.return_value = []
            elif "contributors" in url:
                if params and params.get("page", 1) == 1:
                    response.json.return_value = [
                        {
                            "login": f"contributor{i}",
                            "contributions": 30 - i * 5
                        }
                        for i in range(5)
                    ]
                else:
                    response.json.return_value = []
            else:
                response.json.return_value = {}
            
            return response
        
        mock_session.get.side_effect = mock_get
        
        # Create analyzer and run full analysis
        config = Config(load_dotenv_file=False)
        analyzer = HealthAnalyzer(config)
        
        report = analyzer.analyze_repository("test-owner", "test-repo")
        
        # Verify report structure
        assert report is not None
        assert report.repository == "test-owner/test-repo"
        assert report.health_score is not None
        assert 0 <= report.health_score.overall <= 100
        
        # Verify all metrics are present
        assert report.activity_metrics is not None
        assert report.issue_metrics is not None
        assert report.churn_metrics is not None
        assert report.contributor_metrics is not None
        
        # Verify metrics have reasonable values
        assert report.activity_metrics.commits_last_30_days >= 0
        assert report.issue_metrics.total_open_issues >= 0
        assert report.churn_metrics.total_files_changed >= 0
        assert report.contributor_metrics.total_contributors >= 0
        
        # Verify report can be converted to dict
        report_dict = report.to_dict()
        assert "repository" in report_dict
        assert "health_score" in report_dict
        assert "analyzed_at" in report_dict
    
    def test_config_merging(self):
        """Test that config merging works correctly."""
        config = Config(load_dotenv_file=False)
        
        # Check that weights exist and are valid
        weights = config.get("scoring.weights")
        assert weights is not None
        assert "activity" in weights
        assert "issue_health" in weights
        assert "code_quality" in weights
        assert "contributor_health" in weights
        
        # Check that weights are reasonable values
        assert 0 < weights["activity"] <= 1
        assert 0 < weights["issue_health"] <= 1
        assert 0 < weights["code_quality"] <= 1
        assert 0 < weights["contributor_health"] <= 1
    
    @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token_test"})
    def test_client_initialization_with_env(self):
        """Test that GitHub client properly reads from environment."""
        client = GitHubClient()
        assert client.token == "env_token_test"
        assert client.headers["Authorization"] == "token env_token_test"
