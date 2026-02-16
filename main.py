"""
Main entry point for GitHub Project Health Analyzer (GPHA).

This script provides a simple way to run GPHA analysis programmatically.
For CLI usage, use: python -m gpha.cli
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

from gpha import HealthAnalyzer
from gpha.config import Config


def check_environment():
    """Check if environment is properly configured."""
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded environment from {env_file}")
    
    # Check for GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("\nWARNING: GITHUB_TOKEN not found!")
        print("Please set your GitHub token:")
        print("  1. Create a .env file with: GITHUB_TOKEN=your_token_here")
        print("  2. Or export it: export GITHUB_TOKEN=your_token_here")
        print("\nGet a token at: https://github.com/settings/tokens")
        return False
    
    print(f"✓ GitHub token found (length: {len(token)})")
    return True


def analyze_repository(owner: str, repo: str, output_file: str = None):
    """
    Analyze a GitHub repository and display results.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        output_file: Optional path to save JSON report
    """
    print("\n" + "=" * 70)
    print(f"GitHub Project Health Analysis")
    print("=" * 70)
    print(f"\nRepository: {owner}/{repo}")
    print("Starting analysis...\n")
    
    try:
        # Initialize analyzer
        config = Config()
        analyzer = HealthAnalyzer(config)
        
        # Run analysis
        report = analyzer.analyze_repository(owner, repo)
        
        # Display results
        print("\n" + "=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)
        
        print(f"\nOVERALL HEALTH SCORE: {report.health_score.overall}/100")
        
        # Determine health status
        if report.health_score.overall >= 80:
            status = "[EXCELLENT]"
        elif report.health_score.overall >= 60:
            status = "[GOOD]"
        elif report.health_score.overall >= 40:
            status = "[FAIR]"
        else:
            status = "[NEEDS ATTENTION]"
        
        print(f"Status: {status}\n")
        
        print("Component Scores:")
        print(f"  Activity:           {report.health_score.activity}/100")
        print(f"  Issue Health:       {report.health_score.issue_health}/100")
        print(f"  Code Quality:       {report.health_score.code_quality}/100")
        print(f"  Contributor Health: {report.health_score.contributor_health}/100")
        
        print("\nKey Metrics (Last 30 days):")
        print(f"  Commits:               {report.activity_metrics.commits_last_30_days}")
        print(f"  Pull Requests Opened:  {report.activity_metrics.prs_opened_last_30_days}")
        print(f"  Pull Requests Merged:  {report.activity_metrics.prs_merged_last_30_days}")
        print(f"  Issues Opened:         {report.activity_metrics.issues_opened_last_30_days}")
        print(f"  Issues Closed:         {report.activity_metrics.issues_closed_last_30_days}")
        print(f"  Active Contributors:   {report.activity_metrics.active_contributors_last_30_days}")
        
        print("\nIssue Health:")
        print(f"  Total Open Issues:     {report.issue_metrics.total_open_issues}")
        print(f"  Stagnant (90+ days):   {report.issue_metrics.stagnant_issues_90_days}")
        print(f"  Avg Time to Close:     {report.issue_metrics.avg_time_to_close_days:.1f} days")
        print(f"  Median Issue Age:      {report.issue_metrics.median_issue_age_days:.1f} days")
        
        print("\nCode Churn:")
        print(f"  Files Changed:         {report.churn_metrics.total_files_changed}")
        print(f"  Lines Added:           {report.churn_metrics.total_additions}")
        print(f"  Lines Deleted:         {report.churn_metrics.total_deletions}")
        print(f"  Avg Changes/Commit:    {report.churn_metrics.avg_changes_per_commit:.1f}")
        
        print("\nContributors:")
        print(f"  Total Contributors:    {report.contributor_metrics.total_contributors}")
        print(f"  Active (30 days):      {report.contributor_metrics.active_contributors_30_days}")
        print(f"  New (30 days):         {report.contributor_metrics.new_contributors_30_days}")
        print(f"  Core Contributors:     {report.contributor_metrics.core_contributors}")
        print(f"  Bus Factor:            {report.contributor_metrics.bus_factor}")
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            
            print(f"\nReport saved to: {output_path}")
        
        print("\n" + "=" * 70)
        print("Analysis complete!")
        print("=" * 70 + "\n")
        
        return report
        
    except ValueError as e:
        print(f"\nError: {e}")
        print("Make sure GITHUB_TOKEN is set correctly.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    print("\nGitHub Project Health Analyzer (GPHA)")
    print(f"Version: 0.1.0\n")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Example usage - modify these values or read from command line
    if len(sys.argv) >= 3:
        # Usage: python main.py owner repo [output.json]
        owner = sys.argv[1]
        repo = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Default example
        print("\nUsage: python main.py <owner> <repo> [output.json]")
        print("Example: python main.py microsoft vscode report.json\n")
        
        # You can uncomment and modify this to analyze a specific repo
        # owner = "microsoft"
        # repo = "vscode"
        # output_file = "reports/analysis.json"
        
        print("Please provide repository owner and name as arguments.")
        print("Or modify main.py to set default values.\n")
        sys.exit(0)
    
    # Run analysis
    analyze_repository(owner, repo, output_file)


if __name__ == "__main__":
    main()
