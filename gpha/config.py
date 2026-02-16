"""
Configuration management for GPHA.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration handler for GPHA."""
    
    DEFAULT_CONFIG = {
        "github": {
            "token": None,
            "api_url": "https://api.github.com",
        },
        "analysis": {
            "activity_period_days": 90,
            "stagnation_threshold_days": 90,
            "churn_period_days": 90,
        },
        "scoring": {
            "weights": {
                "activity": 0.30,
                "issue_health": 0.25,
                "code_quality": 0.25,
                "contributor_health": 0.20,
            }
        },
        "output": {
            "format": "json",  # json, yaml, or text
            "save_reports": True,
            "reports_dir": "reports",
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, load_dotenv_file: bool = True):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses default config.
            load_dotenv_file: If True, automatically loads .env file from project root.
        """
        # Load .env file first (if it exists)
        if load_dotenv_file:
            self._load_dotenv_file()
        
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        
        # Override with environment variables
        self._load_from_env()
    
    def load_from_file(self, config_path: str):
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            self._merge_config(user_config)
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with defaults."""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def _load_dotenv_file(self):
        """
        Load .env file from project root.
        
        Searches for .env file in:
        1. Current working directory
        2. Directory containing this file (gpha package)
        3. Parent directory of gpha package (project root)
        """
        # Try current directory first
        cwd_env = Path.cwd() / ".env"
        if cwd_env.exists():
            load_dotenv(cwd_env)
            return
        
        # Try package directory
        package_dir = Path(__file__).parent
        package_env = package_dir / ".env"
        if package_env.exists():
            load_dotenv(package_env)
            return
        
        # Try project root (parent of package)
        project_root = package_dir.parent
        root_env = project_root / ".env"
        if root_env.exists():
            load_dotenv(root_env)
            return
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.config["github"]["token"] = github_token
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key.
        
        Example: config.get("github.token")
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save(self, config_path: str):
        """Save current configuration to file."""
        with open(config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
