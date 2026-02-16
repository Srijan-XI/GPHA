"""
Command-line interface for GPHA.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .analyzer import HealthAnalyzer
from .config import Config
from .models import AnalysisReport


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GitHub Project Health Analyzer - Analyze repository health metrics"
    )
    
    parser.add_argument(
        "repository",
        help="Repository to analyze in format 'owner/repo' (e.g., 'microsoft/vscode')"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file (YAML)",
        default=None
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
        default=None
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "-t", "--token",
        help="GitHub personal access token (overrides config and env)",
        default=None
    )
    
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save detailed report to reports directory"
    )
    
    return parser.parse_args()


def format_text_report(report: AnalysisReport) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"GitHub Project Health Analysis: {report.repository}")
    lines.append("=" * 70)
    lines.append("")
    
    # Overall health
    lines.append(f"OVERALL HEALTH SCORE: {report.health_score.overall}/100")
    lines.append("")
    
    # Component scores
    lines.append("Component Scores:")
    lines.append(f"  - Activity:           {report.health_score.activity}/100")
    lines.append(f"  - Issue Health:       {report.health_score.issue_health}/100")
    lines.append(f"  - Code Quality:       {report.health_score.code_quality}/100")
    lines.append(f"  - Contributor Health: {report.health_score.contributor_health}/100")
    lines.append("")
    
    # Activity metrics
    lines.append("Repository Activity (Last 30 days):")
    lines.append(f"  - Commits:            {report.activity_metrics.commits_last_30_days}")
    lines.append(f"  - PRs Opened:         {report.activity_metrics.prs_opened_last_30_days}")
    lines.append(f"  - PRs Merged:         {report.activity_metrics.prs_merged_last_30_days}")
    lines.append(f"  - Issues Opened:      {report.activity_metrics.issues_opened_last_30_days}")
    lines.append(f"  - Issues Closed:      {report.activity_metrics.issues_closed_last_30_days}")
    lines.append(f"  - Active Contributors: {report.activity_metrics.active_contributors_last_30_days}")
    lines.append("")
    
    # Issue metrics
    lines.append("Issue Health:")
    lines.append(f"  - Total Open Issues:  {report.issue_metrics.total_open_issues}")
    lines.append(f"  - Stagnant (30d):     {report.issue_metrics.stagnant_issues_30_days}")
    lines.append(f"  - Stagnant (90d):     {report.issue_metrics.stagnant_issues_90_days}")
    lines.append(f"  - Stagnant (180d):    {report.issue_metrics.stagnant_issues_180_days}")
    lines.append(f"  - Avg Time to Close:  {report.issue_metrics.avg_time_to_close_days:.1f} days")
    lines.append(f"  - Median Issue Age:   {report.issue_metrics.median_issue_age_days:.1f} days")
    lines.append("")
    
    # Contributor metrics
    lines.append("Contributor Health:")
    lines.append(f"  - Total Contributors: {report.contributor_metrics.total_contributors}")
    lines.append(f"  - Active (30d):       {report.contributor_metrics.active_contributors_30_days}")
    lines.append(f"  - New (30d):          {report.contributor_metrics.new_contributors_30_days}")
    lines.append(f"  - Core Contributors:  {report.contributor_metrics.core_contributors}")
    lines.append(f"  - Bus Factor:         {report.contributor_metrics.bus_factor}")
    lines.append("")
    
    # Code churn
    lines.append("Code Churn (Last 90 days):")
    lines.append(f"  - Files Changed:      {report.churn_metrics.total_files_changed}")
    lines.append(f"  - Lines Added:        {report.churn_metrics.total_additions}")
    lines.append(f"  - Lines Deleted:      {report.churn_metrics.total_deletions}")
    lines.append(f"  - Avg Changes/Commit: {report.churn_metrics.avg_changes_per_commit:.1f}")
    lines.append(f"  - High Churn Files:   {len(report.churn_metrics.files_with_high_churn)}")
    lines.append("")
    
    lines.append("=" * 70)
    lines.append(f"Report generated: {report.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Parse repository
    if "/" not in args.repository:
        print("Error: Repository must be in format 'owner/repo'", file=sys.stderr)
        sys.exit(1)
    
    owner, repo = args.repository.split("/", 1)
    
    try:
        # Initialize configuration
        config = Config(config_path=args.config)
        
        # Override token if provided
        if args.token:
            config.config["github"]["token"] = args.token
        
        # Initialize analyzer
        analyzer = HealthAnalyzer(config)
        
        # Run analysis
        report = analyzer.analyze_repository(owner, repo)
        
        # Format output
        if args.format == "json":
            output = json.dumps(report.to_dict(), indent=2)
        else:
            output = format_text_report(report)
        
        # Write output
        if args.output:
            Path(args.output).write_text(output)
            print(f"\nReport saved to: {args.output}")
        else:
            print("\n" + output)
        
        # Save detailed report if requested
        if args.save_report:
            reports_dir = Path(config.get("output.reports_dir", "reports"))
            reports_dir.mkdir(exist_ok=True)
            
            filename = f"{owner}_{repo}_{report.analyzed_at.strftime('%Y%m%d_%H%M%S')}.json"
            report_path = reports_dir / filename
            
            report_path.write_text(json.dumps(report.to_dict(), indent=2))
            print(f"Detailed report saved to: {report_path}")
        
        # Exit with status based on health score
        if report.health_score.overall >= 80:
            sys.exit(0)  # Excellent health
        elif report.health_score.overall >= 60:
            sys.exit(0)  # Good health
        else:
            sys.exit(1)  # Needs attention
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
