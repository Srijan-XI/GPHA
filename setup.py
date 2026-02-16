"""
Setup configuration for GitHub Project Health Analyzer.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="gpha",
    version="0.1.0",
    description="GitHub Project Health Analyzer - Analyze repository health metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Srijan Kumar",
    author_email="shreejansamsung@gmail.com",
    url="https://github.com/Srijan-XI/gpha",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0.1",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gpha=gpha.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
