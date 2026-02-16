"""
Tests for GitHubClient.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from gpha.github_client import GitHubClient


class TestGitHubClient:
    """Tests for GitHubClient."""
    
    def test_init_with_token(self):
        """Test initialization with explicit token."""
        client = GitHubClient(token="test_token")
        assert client.token == "test_token"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "token test_token"
    
    def test_init_from_env(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            client = GitHubClient()
            assert client.token == "env_token"
    
    def test_init_no_token_raises(self):
        """Test that missing token raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubClient()
    
    @patch("requests.Session")
    def test_get_repo(self, mock_session_class):
        """Test getting repository information."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {"name": "test-repo", "full_name": "owner/test-repo"}
        mock_session.get.return_value = mock_response
        
        client = GitHubClient(token="test_token")
        result = client.get_repo("owner", "test-repo")
        
        assert result["name"] == "test-repo"
        mock_session.get.assert_called_once()
    
    @patch("requests.Session")
    def test_get_commits(self, mock_session_class):
        """Test getting commits."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock pagination - first call returns data, second returns empty
        mock_response_page1 = Mock()
        mock_response_page1.json.return_value = [{'sha': 'abc123'}]
        mock_response_page2 = Mock()
        mock_response_page2.json.return_value = []
        
        mock_session.get.side_effect = [mock_response_page1, mock_response_page2]
        
        client = GitHubClient(token="test_token")
        result = client.get_commits("owner", "repo")
        
        assert len(result) == 1
        assert result[0]["sha"] == "abc123"
    
    @patch("requests.Session")
    def test_get_issues(self, mock_session_class):
        """Test getting issues."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock pagination - first call returns data, second returns empty
        mock_response_page1 = Mock()
        mock_response_page1.json.return_value = [{"number": 1, "state": "open"}]
        mock_response_page2 = Mock()
        mock_response_page2.json.return_value = []
        
        mock_session.get.side_effect = [mock_response_page1, mock_response_page2]
        
        client = GitHubClient(token="test_token")
        result = client.get_issues("owner", "repo")
        
        assert len(result) == 1
        assert result[0]["number"] == 1
