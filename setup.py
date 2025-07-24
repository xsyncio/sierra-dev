from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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

dev_requirements: list[str] = ["setuptools==80.9.0", "ruff==0.12.4"]

requirements: list[str] = ["colorama==0.4.6", "httpx==0.28.1"]

setup(
    name="sierra-dev",
    version="0.1.2",
    author="Xsyncio",
    description="A framework for building and managing invoker scripts across different nodes in Sierra.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xsyncio/sierra-dev",
    project_urls={
        "Documentation": "https://xsyncio.github.io/sierra-dev",
        "Source": "https://github.com/xsyncio/sierra-dev",
        "Tracker": "https://github.com/xsyncio/sierra-dev/issues",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={"dev": dev_requirements, "docs": mkdocs_requirements},
    include_package_data=True,
    package_data={
        "": [
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            "dev-requirements.txt",
            "mkdocs-requirements.txt",
        ],
    },
    entry_points={
        "console_scripts": [
            "sierra-dev=__main__:cli",
        ],
    },
    keywords="sierra, invoker, script, framework",
)
