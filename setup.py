#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README_GENERIC.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="newsletter-automation",
    version="1.0.0",
    author="Newsletter Automation Contributors",
    description="Automate newsletter processing with AI synthesis, Notion, and Gmail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votreusername/newsletter-automation",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "newsletter-automation=src.newsletter_automation.newsletter_automation:main",
        ],
    },
)
