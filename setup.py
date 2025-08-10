#!/usr/bin/env python3
"""
Setup configuration for PDF Dark Mode Converter
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "PDF Dark Mode Converter & Merger - Convert PDFs to dark theme and merge multiple documents"

# Read requirements
requirements = []
req_path = Path(__file__).parent / "requirements.txt"
if req_path.exists():
    with open(req_path, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pdf-dark-converter",
    version="1.0.0",
    description="Convert PDF documents to dark theme and merge multiple PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PDF Tools Developer",
    author_email="developer@pdftools.com",
    url="https://github.com/pdftools/pdf-dark-converter",
    license="MIT",
    
    # Package configuration
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    
    # Entry points
    entry_points={
        "console_scripts": [
            "pdf-dark-converter=main:main",
        ],
        "gui_scripts": [
            "pdf-dark-converter-gui=main:main",
        ]
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": ["*.ico", "*.png", "*.txt", "*.md"],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Utilities",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: MacOS X",
    ],
    
    # Keywords for discovery
    keywords=[
        "pdf", "dark-mode", "converter", "merger", "document-processing",
        "theme", "inversion", "desktop-application", "gui"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/pdftools/pdf-dark-converter/issues",
        "Source": "https://github.com/pdftools/pdf-dark-converter",
        "Documentation": "https://github.com/pdftools/pdf-dark-converter/wiki",
    },
)