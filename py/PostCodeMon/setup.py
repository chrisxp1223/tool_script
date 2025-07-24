"""Setup configuration for PostCodeMon."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, encoding="utf-8") as f:
    requirements = [
        line.strip() 
        for line in f 
        if line.strip() and not line.startswith("#") and not line.startswith("-e")
    ]

setup(
    name="PostCodeMon",
    version="0.1.0",
    author="ChromeOS Hardware Team",
    author_email="chromeos-hardware@example.com",
    description="A modern Python wrapper for Windows CLI tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/postcodemon",
    packages=find_packages(include=['PostCodeMon', 'PostCodeMon.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11", 
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "monitoring": [
            "prometheus-client>=0.16.0",
            "requests>=2.28.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "postcodemon=PostCodeMon.cli.main:main",
            "pcm=PostCodeMon.cli.main:main",  # Short alias
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="windows cli wrapper automation devops testing",
    project_urls={
        "Bug Reports": "https://github.com/example/postcodemon/issues",
        "Source": "https://github.com/example/postcodemon",
        "Documentation": "https://postcodemon.readthedocs.io/",
    },
)