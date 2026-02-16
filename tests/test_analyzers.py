"""
Unit tests for GPHA analyzers.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from gpha.analyzers.repo_activity import RepoActivityAnalyzer
from gpha.github_client import GitHubClient


class TestRepoActivityAnalyzer:
    """Tests for RepoActivityAnalyzer."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock GitHub client."""
        client = Mock(spec=GitHubClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_client):
        """Create analyzer with mock client."""
        return RepoActivityAnalyzer(mock_client)
    
    def test_analyze_basic(self, analyzer, mock_client):
        """Test basic analysis functionality."""
        # Mock API responses
        now = datetime.now()
        
        mock_client.get_commits.return_value = [
            {"commit": {"author": {"email": "user1@example.com"}}} for _ in range(20)
        ]
        
        mock_client.get_pull_requests.return_value = [
            {
                "created_at": now.isoformat() + "Z",
                "merged_at": now.isoformat() + "Z"
            }
            for _ in range(5)
        ]
        
        mock_client.get_issues.return_value = [
            {
                "created_at": now.isoformat() + "Z",
                "closed_at": now.isoformat() + "Z"
            }
            for _ in range(3)
        ]
        
        # Run analysis
        metrics = analyzer.analyze("owner", "repo")
        
        # Verify results
        assert metrics.commits_last_30_days == 20
        assert metrics.score > 0
        assert metrics.score <= 100


# Add more tests here...
