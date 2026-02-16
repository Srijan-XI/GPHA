"""
Tests for configuration module.
"""

import pytest
from unittest.mock import patch, mock_open
import yaml

from gpha.config import Config


class TestConfig:
    """Tests for Config class."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = Config()
        
        # Should have default values
        weights = config.get("scoring.weights")
        assert weights is not None
        assert "activity" in weights
    
    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        config = Config()
        
        # Test nested access
        value = config.get("scoring.weights.activity")
        assert value is not None
        
    def test_get_with_default(self):
        """Test getting value with default."""
        config = Config()
        
        # Non-existent key should return default
        value = config.get("non.existent.key", default=42)
        assert value == 42
    
    def test_get_without_default(self):
        """Test getting non-existent value without default."""
        config = Config()
        
        # Non-existent key should return None
        value = config.get("non.existent.key")
        assert value is None
    
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="""
scoring:
  weights:
    activity: 0.35
    issue_health: 0.30
    code_quality: 0.20
    contributor_health: 0.15
github:
  token: custom_token
""")
    def test_load_custom_config(self, mock_file, mock_exists):
        """Test loading custom configuration from file."""
        # Make path exist
        mock_exists.return_value = True
        
        config = Config(config_path="custom_config.yaml", load_dotenv_file=False)
        
        # Should load custom values
        token = config.get("github.token")
        assert token == "custom_token"
        
        activity_weight = config.get("scoring.weights.activity")
        assert activity_weight == 0.35
