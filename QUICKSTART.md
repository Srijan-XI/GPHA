# Quick Start Guide

Get up and running with GPHA in under 5 minutes!

## 1. Prerequisites

- Python 3.8 or higher
- A GitHub account
- Git (optional, for cloning)

## 2. Installation

```bash
# Navigate to the project directory
cd p:\CODE-TOOLS\GPHA

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install GPHA in development mode
pip install -e .
```

## 3. Get Your GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it "GPHA"
4. Select scope: `public_repo` (or `repo` for private repos)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

## 4. Configure Your Token

Create a `.env` file:

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your token:
# GITHUB_TOKEN=ghp_your_token_here
```

Or set it as an environment variable:

```powershell
# Windows PowerShell
$env:GITHUB_TOKEN="ghp_your_token_here"

# Windows CMD
set GITHUB_TOKEN=ghp_your_token_here

# macOS/Linux
export GITHUB_TOKEN=ghp_your_token_here
```

## 5. Run Your First Analysis

```bash
# Analyze a popular repository
gpha microsoft/vscode -f text

# Or try another one
gpha facebook/react -f text

# Save the output to a file
gpha python/cpython -o report.json
```

## 6. Example Output

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

## 7. Next Steps

### Customize Analysis

Edit `config.yaml` to adjust:
- Time periods (30, 60, 90 days)
- Scoring weights
- Output formats

### Use Python API

```python
from gpha import HealthAnalyzer, Config

config = Config()
analyzer = HealthAnalyzer(config)
report = analyzer.analyze_repository("owner", "repo")

print(f"Score: {report.health_score.overall}/100")
```

### Analyze Multiple Repos

```python
repos = ["microsoft/vscode", "facebook/react", "vuejs/vue"]

for repo in repos:
    owner, name = repo.split("/")
    report = analyzer.analyze_repository(owner, name)
    print(f"{repo}: {report.health_score.overall}/100")
```

## Common Issues

### "No module named gpha"
Make sure you've installed the package:
```bash
pip install -e .
```

### "GitHub token is required"
Check that your token is set:
```bash
# Windows
echo %GITHUB_TOKEN%

# PowerShell
echo $env:GITHUB_TOKEN

# macOS/Linux
echo $GITHUB_TOKEN
```

### Rate Limit Errors
GitHub API has rate limits. Check your remaining requests:
```python
from gpha import GitHubClient
client = GitHubClient()
print(client.get_rate_limit())
```

## Getting Help

- Check the full [README.md](README.md)
- See [examples.md](docs/examples.md) for more examples
- Run `gpha --help` for CLI options

## Ready to Go!

You're all set! Start analyzing repositories and discovering insights into project health.

```bash
# Analyze your own repository
gpha yourusername/your-repo --save-report

# Compare multiple projects
gpha microsoft/typescript -f text
gpha python/mypy -f text
gpha facebook/flow -f text
```

Happy analyzing! 🚀
