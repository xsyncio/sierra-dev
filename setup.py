from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# MkDocs documentation dependencies
mkdocs_requirements: list[str] = [
    "mkdocs==1.6.1",
    "mkdocs-autorefs==1.4.2",
    "mkdocs-dracula-theme==1.0.7",
    "mkdocs-get-deps==0.2.0",
    "mkdocs-git-committers-plugin-2==2.5.0",
    "mkdocs-git-revision-date-localized-plugin==1.4.7",
    "mkdocs-glightbox==0.4.0",
    "mkdocs-llmstxt==0.3.0",
    "mkdocs-material==9.6.15",
    "mkdocs-material-extensions==1.3.1",
    "mkdocs-minify-plugin==0.8.0",
    "mkdocs-print-site-plugin==2.7.3",
    "mkdocs-social-plugin==0.1.0",
    "mkdocs-with-pdf==0.9.3",
    "mkdocstrings==0.29.1",
    "mkdocstrings-python==1.16.12",
    "pymdown-extensions==10.16",
    "Markdown==3.8.2",
    "markdown-it-py==3.0.0",
    "markdownify==1.1.0",
    "jupyterlab_pygments==0.3.0",
    "Pygments==2.19.2",
]

# Development dependencies (linting, testing, formatting)
dev_requirements: list[str] = [
    "setuptools==80.9.0",
    "ruff==0.12.4",
    "pytest==8.0.0",
    "pytest-cov==4.1.0",
    "pytest-mock==3.12.0",
    "black==24.3.0",
    "mypy==1.8.0",
]

# Core runtime dependencies
requirements: list[str] = [
    "colorama==0.4.6",  # Terminal colors
    "httpx==0.28.1",     # HTTP client for package manager
    "dnspython==2.6.1",  # DNS operations for OSINT tools
    "requests==2.32.0",  # HTTP requests for OSINT tools
    "beautifulsoup4==4.12.3",  # HTML parsing for tech detection
]

setup(
    name="sierra-dev",
    version="2.1.0",
    author="Xsyncio",
    author_email="dev@xsyncio.com",
    description="Sierra Dev - Modern Invoker Package Manager and Development Framework",
    description="Modern framework for building investigation invoker scripts with APT-like package management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xsyncio/sierra-dev",
    project_urls={
        "Documentation": "https://xsyncio.github.io/sierra-dev",
        "Source": "https://github.com/xsyncio/sierra-dev",
        "Tracker": "https://github.com/xsyncio/sierra-dev/issues",
        "Changelog": "https://github.com/xsyncio/sierra-dev/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests*", "docs*", "example*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "docs": mkdocs_requirements,
        "full": requirements + dev_requirements + mkdocs_requirements,
    },
    include_package_data=True,
    package_data={
        "sierra": ["py.typed"],
        "": [
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            "dev-requirements.txt",
        ],
    },
    entry_points={
        "console_scripts": [
            "sierra-dev=sierra.cli:main",
        ],
    },
    keywords=[
        "sierra-dev",
        "sierra",
        "invoker",
        "script",
        "framework",
        "osint",
        "package-manager",
        "investigation",
        "security",
        "automation",
        "cli",
    ],
    zip_safe=False,
)
