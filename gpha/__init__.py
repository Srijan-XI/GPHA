"""
GitHub Project Health Analyzer (GPHA)

A comprehensive tool for analyzing GitHub repository health metrics.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .analyzers.repo_activity import RepoActivityAnalyzer
from .analyzers.issue_stagnation import IssueStagnationAnalyzer
from .analyzers.code_churn import CodeChurnAnalyzer
from .analyzers.contributor_patterns import ContributorPatternsAnalyzer
from .github_client import GitHubClient

__all__ = [
    "RepoActivityAnalyzer",
    "IssueStagnationAnalyzer",
    "CodeChurnAnalyzer",
    "ContributorPatternsAnalyzer",
    "GitHubClient",
]
