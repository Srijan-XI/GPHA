"""
GitHub API client for GPHA.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token. If None, will try to get from env.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN env variable or pass token.")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_commits(self, owner: str, repo: str, since: Optional[datetime] = None, 
                    until: Optional[datetime] = None, per_page: int = 100) -> list:
        """Get repository commits."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": per_page}
        
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()
        
        commits = []
        page = 1
        
        while True:
            params["page"] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            commits.extend(data)
            page += 1
            
            # Limit to prevent excessive API calls
            if page > 10:  # Max 1000 commits
                break
        
        return commits
    
    def get_issues(self, owner: str, repo: str, state: str = "all", 
                   since: Optional[datetime] = None, per_page: int = 100) -> list:
        """Get repository issues."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": per_page}
        
        if since:
            params["since"] = since.isoformat()
        
        issues = []
        page = 1
        
        while True:
            params["page"] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            # Filter out pull requests (they appear in issues endpoint)
            issues.extend([issue for issue in data if "pull_request" not in issue])
            page += 1
            
            if page > 10:
                break
        
        return issues
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "all", 
                          per_page: int = 100) -> list:
        """Get repository pull requests."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": per_page}
        
        prs = []
        page = 1
        
        while True:
            params["page"] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            prs.extend(data)
            page += 1
            
            if page > 10:
                break
        
        return prs
    
    def get_contributors(self, owner: str, repo: str, per_page: int = 100) -> list:
        """Get repository contributors."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": per_page}
        
        contributors = []
        page = 1
        
        while True:
            params["page"] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            contributors.extend(data)
            page += 1
            
            if page > 5:
                break
        
        return contributors
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current API rate limit status."""
        url = f"{self.base_url}/rate_limit"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
