#!/usr/bin/env python
"""
Setup script for NoDox package.
For modern Python packaging, use pyproject.toml instead.
This file is kept for backwards compatibility.
"""

from setuptools import setup, find_packages
import os

# Leer README para descripción larga
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "NoDox - Neutralizing Doxware & Modern Ransomware Extortion"


# Leer requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return ["cryptography>=43.0.0", "pyyaml>=6.0.1", "psutil>=6.0.0"]


setup(
    name="nodox",
    version="0.2.0",
    author="NoDox Team",
    author_email="nodox@example.com",
    description="NoDox - Neutralizing Doxware & Modern Ransomware Extortion",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Orantes67/NoDox",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "nodox": ["config/*.yaml", "config/*.txt"],
    },
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nodox=nodox.nodox:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.10",
    keywords="security ransomware doxware encryption data-protection cybersecurity",
)
