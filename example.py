"""
Example script showing how to use GPHA programmatically.
"""

from gpha import HealthAnalyzer, Config


def main():
    """Run example analysis."""
    
    # Initialize with default config
    config = Config()
    analyzer = HealthAnalyzer(config)
    
    # Analyze a popular repository
    print("Analyzing microsoft/vscode...")
    report = analyzer.analyze_repository("microsoft", "vscode")
    
    # Display summary
    print("\n" + "=" * 70)
    print(f"Repository: {report.repository}")
    print(f"Overall Health Score: {report.health_score.overall}/100")
    print("=" * 70)
    
    print("\nComponent Scores:")
    print(f"  Activity:           {report.health_score.activity}/100")
    print(f"  Issue Health:       {report.health_score.issue_health}/100")
    print(f"  Code Quality:       {report.health_score.code_quality}/100")
    print(f"  Contributor Health: {report.health_score.contributor_health}/100")
    
    print("\nKey Metrics:")
    print(f"  Commits (30d):      {report.activity_metrics.commits_last_30_days}")
    print(f"  Active Contributors: {report.activity_metrics.active_contributors_last_30_days}")
    print(f"  Open Issues:        {report.issue_metrics.total_open_issues}")
    print(f"  Stagnant Issues:    {report.issue_metrics.stagnant_issues_90_days}")
    print(f"  Bus Factor:         {report.contributor_metrics.bus_factor}")
    
    # Export to JSON
    import json
    print("\nFull report available as JSON:")
    print(json.dumps(report.to_dict(), indent=2)[:500] + "...")


if __name__ == "__main__":
    main()
