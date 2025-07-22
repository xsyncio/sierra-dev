from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sierra-dev",
    version="0.1.0",
    author="Xsyncio",
    author_email="xsyncio@gmail.com",
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
    install_requires=[
        "httpx>=0.21.0,<1.0.0",  # Replace with actual dependencies and versions
    ],
    extras_require={
        "dev": ["pytest>=6.0.0", "black>=22.0.0", "mypy>=0.910"],
        "docs": ["sphinx", "sphinx_rtd_theme"],
    },
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md"],
    },
    entry_points={
        "console_scripts": [
            "sierra-cli=sierra.cli:main",
        ],
    },
    keywords="sierra, invoker, script, framework",
)
