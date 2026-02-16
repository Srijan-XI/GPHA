# Example Usage

This document provides detailed examples of using the GitHub Project Health Analyzer.

## Basic Analysis

### Analyze a Popular Repository

```bash
# Analyze the VS Code repository
gpha microsoft/vscode -f text
```

### Analyze Multiple Repositories

```bash
#!/bin/bash
# analyze_repos.sh

repos=(
    "microsoft/vscode"
    "facebook/react"
    "python/cpython"
    "torvalds/linux"
)

for repo in "${repos[@]}"; do
    echo "Analyzing $repo..."
    gpha "$repo" --save-report
done
```

## Python API Examples

### Basic Analysis

```python
from gpha import HealthAnalyzer, Config

# Initialize
config = Config()
analyzer = HealthAnalyzer(config)

# Analyze
report = analyzer.analyze_repository("microsoft", "typescript")

# Display results
print(f"Repository: {report.repository}")
print(f"Overall Health: {report.health_score.overall}/100")
```

### Custom Configuration

```python
from gpha import HealthAnalyzer, Config

# Create custom config
config = Config()
config.config["analysis"]["churn_period_days"] = 30
config.config["scoring"]["weights"]["activity"] = 0.40
config.config["scoring"]["weights"]["contributor_health"] = 0.10

analyzer = HealthAnalyzer(config)
report = analyzer.analyze_repository("facebook", "react")
```

### Analyze Multiple Repositories

```python
from gpha import HealthAnalyzer, Config
import json

repos = [
    ("microsoft", "vscode"),
    ("facebook", "react"),
    ("vuejs", "vue"),
    ("angular", "angular"),
]

config = Config()
analyzer = HealthAnalyzer(config)

results = []
for owner, repo in repos:
    try:
        report = analyzer.analyze_repository(owner, repo)
        results.append({
            "repo": f"{owner}/{repo}",
            "score": report.health_score.overall,
            "metrics": report.to_dict()
        })
    except Exception as e:
        print(f"Error analyzing {owner}/{repo}: {e}")

# Sort by score
results.sort(key=lambda x: x["score"], reverse=True)

# Display rankings
print("\nRepository Health Rankings:")
print("=" * 50)
for i, result in enumerate(results, 1):
    print(f"{i}. {result['repo']}: {result['score']}/100")
```

### Export Report

```python
from gpha import HealthAnalyzer, Config
import json
from pathlib import Path

config = Config()
analyzer = HealthAnalyzer(config)

report = analyzer.analyze_repository("microsoft", "vscode")

# Export as JSON
output_path = Path("vscode_health_report.json")
output_path.write_text(json.dumps(report.to_dict(), indent=2))

print(f"Report saved to {output_path}")
```

### Focus on Specific Metrics

```python
from gpha import HealthAnalyzer, Config

config = Config()
analyzer = HealthAnalyzer(config)

report = analyzer.analyze_repository("python", "cpython")

# Check issue stagnation
print("Issue Stagnation Analysis:")
print(f"Total open issues: {report.issue_metrics.total_open_issues}")
print(f"Stagnant (90+ days): {report.issue_metrics.stagnant_issues_90_days}")
print(f"Stagnation rate: {report.issue_metrics.stagnant_issues_90_days / report.issue_metrics.total_open_issues * 100:.1f}%")

# Check contributor diversity
print("\nContributor Analysis:")
print(f"Bus factor: {report.contributor_metrics.bus_factor}")
print(f"Active contributors: {report.contributor_metrics.active_contributors_30_days}")
print(f"New contributors: {report.contributor_metrics.new_contributors_30_days}")
```

### Compare Repositories

```python
from gpha import HealthAnalyzer, Config

def compare_repos(repo1, repo2):
    config = Config()
    analyzer = HealthAnalyzer(config)
    
    report1 = analyzer.analyze_repository(*repo1.split("/"))
    report2 = analyzer.analyze_repository(*repo2.split("/"))
    
    print(f"\nComparison: {repo1} vs {repo2}")
    print("=" * 60)
    
    metrics = [
        ("Overall Health", "health_score.overall"),
        ("Activity", "health_score.activity"),
        ("Issue Health", "health_score.issue_health"),
        ("Code Quality", "health_score.code_quality"),
        ("Contributor Health", "health_score.contributor_health"),
    ]
    
    for name, path in metrics:
        # Get nested attribute
        val1 = report1
        val2 = report2
        for attr in path.split("."):
            val1 = getattr(val1, attr)
            val2 = getattr(val2, attr)
        
        diff = val1 - val2
        symbol = ">" if diff > 0 else "<" if diff < 0 else "="
        
        print(f"{name:20s}: {val1:6.2f} {symbol} {val2:6.2f} (Δ {abs(diff):.2f})")

# Compare two repositories
compare_repos("facebook/react", "vuejs/vue")
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/health-check.yml
name: Repository Health Check

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install GPHA
        run: |
          pip install gpha
      
      - name: Run Health Analysis
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gpha ${{ github.repository }} --save-report -o health_report.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: health-report
          path: health_report.json
```

## Advanced Filtering

### Filter Stagnant Issues

```python
from gpha import HealthAnalyzer, Config

config = Config()
analyzer = HealthAnalyzer(config)

report = analyzer.analyze_repository("apache", "airflow")

# Get stagnant issue numbers
stagnant_issues = report.issue_metrics.stagnant_issue_numbers

print(f"Found {len(stagnant_issues)} stagnant issues (90+ days):")
print(f"Issue numbers: {stagnant_issues[:10]}")  # Show first 10
```

### Identify Code Hotspots

```python
from gpha import HealthAnalyzer, Config

config = Config()
analyzer = HealthAnalyzer(config)

report = analyzer.analyze_repository("django", "django")

print("Code Hotspots (Most Frequently Changed Files):")
for i, hotspot in enumerate(report.churn_metrics.hotspot_files[:5], 1):
    print(f"{i}. {hotspot['file']}")
    print(f"   Changes: {hotspot['changes']} lines")
    print(f"   Commits: {hotspot['commits']}")
```
