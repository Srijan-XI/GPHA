"""
Unit tests for GPHA analyzers.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta, timezone

from gpha.analyzers.repo_activity import RepoActivityAnalyzer
from gpha.analyzers.issue_stagnation import IssueStagnationAnalyzer
from gpha.analyzers.code_churn import CodeChurnAnalyzer
from gpha.analyzers.contributor_patterns import ContributorPatternsAnalyzer
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
    
    def test_analyze_no_activity(self, analyzer, mock_client):
        """Test analysis with no repository activity."""
        mock_client.get_commits.return_value = []
        mock_client.get_pull_requests.return_value = []
        mock_client.get_issues.return_value = []
        
        metrics = analyzer.analyze("owner", "repo")
        
        assert metrics.commits_last_30_days == 0
        assert metrics.prs_opened_last_30_days == 0
        assert metrics.score >= 0


class TestIssueStagnationAnalyzer:
    """Tests for IssueStagnationAnalyzer."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock GitHub client."""
        client = Mock(spec=GitHubClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_client):
        """Create analyzer with mock client."""
        return IssueStagnationAnalyzer(mock_client)
    
    def test_analyze_with_stagnant_issues(self, analyzer, mock_client):
        """Test detection of stagnant issues."""
        now = datetime.now(timezone.utc)
        old_date = (now - timedelta(days=100)).replace(tzinfo=timezone.utc)
        recent_date = (now - timedelta(days=5)).replace(tzinfo=timezone.utc)
        
        mock_client.get_issues.return_value = [
            {
                "number": 1,
                "state": "open",
                "created_at": old_date.isoformat(),
                "updated_at": old_date.isoformat()
            },
            {
                "number": 2,
                "state": "open",
                "created_at": recent_date.isoformat(),
                "updated_at": recent_date.isoformat()
            },
            {
                "number": 3,
                "state": "closed",
                "created_at": old_date.isoformat(),
                "updated_at": recent_date.isoformat(),
                "closed_at": recent_date.isoformat()
            }
        ]
        
        metrics = analyzer.analyze("owner", "repo")
        
        assert metrics.total_open_issues == 2
        assert metrics.stagnant_issues_90_days > 0
        assert metrics.score >= 0
        assert metrics.score <= 100


class TestCodeChurnAnalyzer:
    """Tests for CodeChurnAnalyzer."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock GitHub client."""
        client = Mock(spec=GitHubClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_client):
        """Create analyzer with mock client."""
        return CodeChurnAnalyzer(mock_client)
    
    def test_analyze_basic(self, analyzer, mock_client):
        """Test basic code churn analysis."""
        # Mock commits with stats
        mock_client.get_commits.return_value = [
            {
                "sha": "sha1",
                "stats": {
                    "additions": 100,
                    "deletions": 50
                },
                "files": [
                    {
                        "filename": "file1.py",
                        "additions": 100,
                        "deletions": 50,
                        "changes": 150
                    }
                ]
            },
            {
                "sha": "sha2",
                "stats": {
                    "additions": 20,
                    "deletions": 10
                },
                "files": [
                    {
                        "filename": "file2.py",
                        "additions": 20,
                        "deletions": 10,
                        "changes": 30
                    }
                ]
            }
        ]
        
        metrics = analyzer.analyze("owner", "repo", days=30)
        
        assert metrics.total_files_changed >= 0
        assert metrics.total_additions >= 0
        assert metrics.score >= 0


class TestContributorPatternsAnalyzer:
    """Tests for ContributorPatternsAnalyzer."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock GitHub client."""
        client = Mock(spec=GitHubClient)
        return client
    
    @pytest.fixture
    def analyzer(self, mock_client):
        """Create analyzer with mock client."""
        return ContributorPatternsAnalyzer(mock_client)
    
    def test_analyze_contributors(self, analyzer, mock_client):
        """Test contributor pattern analysis."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(days=15)
        
        # Mock contributors list
        mock_client.get_contributors.return_value = [
            {"login": "user1", "contributions": 15},
            {"login": "user2", "contributions": 5}
        ]
        
        # Mock commits
        mock_client.get_commits.return_value = [
            {
                "commit": {
                    "author": {
                        "email": "user1@example.com",
                        "date": recent.isoformat()
                    }
                }
            } for _ in range(15)
        ] + [
            {
                "commit": {
                    "author": {
                        "email": "user2@example.com",
                        "date": recent.isoformat()
                    }
                }
            } for _ in range(5)
        ]
        
        metrics = analyzer.analyze("owner", "repo")
        
        assert metrics.total_contributors >= 0
        assert metrics.score >= 0
        assert metrics.score <= 100
