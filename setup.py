#!/usr/bin/env python3
"""
Setup script for NDB CSV Processor
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ndb-csv-processor",
    version="2.0.0",
    author="Hadi Fauzan Hanif",
    author_email="",  # Email removed for privacy
    description="Advanced Network Database CSV Processing Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hadifauzan/ndb-csv-processor",
    project_urls={
        "Bug Tracker": "https://github.com/hadifauzan/ndb-csv-processor/issues",
        "Documentation": "https://github.com/hadifauzan/ndb-csv-processor/blob/main/README.md",
        "Source Code": "https://github.com/hadifauzan/ndb-csv-processor",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: MacOS X",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ndb-csv-processor=ndb_processor_gui:main",
        ],
    },
    keywords=[
        "csv", "processor", "network", "database", "telecommunications", 
        "data-processing", "gui", "pandas", "dear-pygui"
    ],
    include_package_data=True,
    zip_safe=False,
) 