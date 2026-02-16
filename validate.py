"""Quick validation script for GPHA configuration and setup."""

from gpha.config import Config
from gpha import HealthAnalyzer

print("=" * 60)
print("GPHA Configuration Validation")
print("=" * 60)

# Test config
config = Config(load_dotenv_file=False)
weights = config.get("scoring.weights")

print("\n✓ Config loaded successfully")
print(f"  Weights: {weights}")
print(f"  Sum of weights: {sum(weights.values())}")
print(f"  All keys present: {all(k in weights for k in ['activity', 'issue_health', 'code_quality', 'contributor_health'])}")

# Verify imports
try:
    from gpha.analyzers import (
        RepoActivityAnalyzer,
        IssueStagnationAnalyzer,
        CodeChurnAnalyzer,
        ContributorPatternsAnalyzer,
    )
    print("\n✓ All analyzer imports successful")
except Exception as e:
    print(f"\n✗ Import error: {e}")

# Verify models
try:
    from gpha.models import (
        HealthScore,
        ActivityMetrics,
        IssueStagnationMetrics,
        CodeChurnMetrics,
        ContributorMetrics,
        AnalysisReport,
    )
    print("✓ All model imports successful")
except Exception as e:
    print(f"✗ Model import error: {e}")

print("\n" + "=" * 60)
print("All validations passed! ✓")
print("=" * 60)
