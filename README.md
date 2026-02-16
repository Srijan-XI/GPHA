# GitHub Project Health Analyzer (GPHA)

A comprehensive Python tool for analyzing GitHub repository health through multiple metrics and scoring dimensions.

## Features

GPHA provides deep insights into repository health through four key analysis areas:

### 🎯 Repository Activity Scoring
- Tracks commits, pull requests, and issues over time
- Measures contributor engagement
- Identifies activity trends and patterns
- Provides weighted scoring based on different activity types

### 🔍 Issue Stagnation Detection
- Identifies issues that haven't been updated in 30, 90, or 180 days
- Calculates average time to close issues
- Analyzes median issue age
- Highlights potential maintenance bottlenecks

### 📊 Code Churn Analysis
- Tracks file-level changes over time
- Identifies code hotspots (frequently changing files)
- Measures additions vs. deletions ratios
- Detects high-churn files that may indicate quality issues

### 👥 Contributor Patterns
- Analyzes contributor diversity and distribution
- Calculates "bus factor" (project dependency on key contributors)
- Tracks new contributor growth
- Identifies core vs. occasional contributors

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Srijan-XI/gpha.git
cd gpha

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Using pip (once published)

```bash
pip install gpha
```

## Setup

### 1. Get a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "GPHA Analysis")
4. Select scopes:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories only)
5. Click "Generate token" and copy the token

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```
GITHUB_TOKEN=your_github_token_here
```

Alternatively, set the environment variable directly:

```bash
export GITHUB_TOKEN=your_github_token_here
```

## Usage

### Command Line Interface

Basic usage:

```bash
# Analyze a public repository
gpha microsoft/vscode

# Analyze with custom config
gpha facebook/react -c config.yaml

# Output to file
gpha owner/repo -o report.json

# Text format output
gpha owner/repo -f text

# Save detailed report
gpha owner/repo --save-report
```

### Python API

```python
from gpha import HealthAnalyzer
from gpha.config import Config

# Initialize analyzer
config = Config()
analyzer = HealthAnalyzer(config)

# Analyze a repository
report = analyzer.analyze_repository("microsoft", "vscode")

# Access metrics
print(f"Overall Health: {report.health_score.overall}/100")
print(f"Activity Score: {report.health_score.activity}/100")
print(f"Active Contributors: {report.activity_metrics.active_contributors_30_days}")
print(f"Stagnant Issues: {report.issue_metrics.stagnant_issues_90_days}")
print(f"Bus Factor: {report.contributor_metrics.bus_factor}")

# Export to dict
report_dict = report.to_dict()
```

## Configuration

Configuration can be provided via `config.yaml`:

```yaml
github:
  token: null  # Use environment variable

analysis:
  activity_period_days: 90
  stagnation_threshold_days: 90
  churn_period_days: 90

scoring:
  weights:
    activity: 0.30
    issue_health: 0.25
    code_quality: 0.25
    contributor_health: 0.20

output:
  format: json
  save_reports: true
  reports_dir: reports
```

## Scoring Methodology

### Overall Health Score (0-100)

The overall score is a weighted combination of four component scores:

- **Activity (30%)**: Based on commit frequency, PR activity, and issue management
- **Issue Health (25%)**: Lower stagnation rates and faster resolution times
- **Code Quality (25%)**: Balanced code churn and distribution of changes
- **Contributor Health (20%)**: Diversity, bus factor, and contributor growth

### Component Scoring Details

#### Activity Score
- 40 points: Commit frequency (10+ commits/month = max)
- 25 points: PR activity (5+ PRs with 80% merge rate = max)
- 20 points: Issue management (high close rate = max)
- 15 points: Active contributors (5+ = max)

#### Issue Health Score
- Starts at 100, penalties for:
  - Stagnation rates (30d, 90d, 180d)
  - Slow average close time
  - High median issue age

#### Code Quality Score
- Starts at 100, penalties for:
  - Excessive churn (>500 lines/commit)
  - Too many hotspot files
  - High deletion-to-addition ratio

#### Contributor Health Score
- 40 points: Active contributors (10+ in 30 days = max)
- 30 points: Bus factor (5+ = max)
- 15 points: Core contributors (5+ = max)
- 15 points: New contributor growth (3+/month = max)

## Example Output

### JSON Format

```json
{
  "repository": "microsoft/vscode",
  "health_score": {
    "overall": 85.5,
    "activity": 88.0,
    "issue_health": 75.0,
    "code_quality": 90.0,
    "contributor_health": 92.0
  },
  "activity_metrics": {
    "commits_last_30_days": 245,
    "active_contributors_last_30_days": 35
  }
}
```

### Text Format

```
======================================================================
GitHub Project Health Analysis: microsoft/vscode
======================================================================

OVERALL HEALTH SCORE: 85.5/100

Component Scores:
  - Activity:           88.0/100
  - Issue Health:       75.0/100
  - Code Quality:       90.0/100
  - Contributor Health: 92.0/100

Repository Activity (Last 30 days):
  - Commits:            245
  - PRs Opened:         78
  - PRs Merged:         65
  - Active Contributors: 35
```

## Project Structure

```
GPHA/
├── gpha/                      # Main package
│   ├── __init__.py
│   ├── analyzer.py            # Main orchestrator
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── github_client.py       # GitHub API client
│   ├── models.py              # Data models
│   └── analyzers/             # Individual analyzers
│       ├── __init__.py
│       ├── repo_activity.py
│       ├── issue_stagnation.py
│       ├── code_churn.py
│       └── contributor_patterns.py
├── tests/                     # Test suite
├── docs/                      # Documentation
├── config.yaml                # Default configuration
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup
└── README.md                  # This file
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black gpha/
flake8 gpha/
```

### Type Checking

```bash
mypy gpha/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

Future enhancements planned:

- [ ] Web dashboard for visualization
- [ ] Historical trend analysis
- [ ] Comparative analysis across multiple repos
- [ ] Integration with CI/CD pipelines
- [ ] Custom scoring weight configurations
- [ ] Export to various formats (PDF, HTML)
- [ ] GitHub Actions integration
- [ ] Team and organization-level analysis

## Acknowledgments

- Built with the GitHub REST API
- Inspired by various open-source health metrics tools
- Thanks to all contributors!

## Support

For issues, questions, or contributions, please visit:
- Issue Tracker: https://github.com/yourusername/gpha/issues
- Discussions: https://github.com/yourusername/gpha/discussions
