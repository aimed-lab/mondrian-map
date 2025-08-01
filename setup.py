"""
Setup script for Mondrian Map package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements_path = this_directory / "config" / "requirements.txt"
with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="mondrian-map",
    version="1.0.0",
    author="Mondrian Map Team",
    author_email="your-email@example.com",
    description="Authentic implementation of Mondrian Maps for biological pathway visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mondrian-map",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "mondrian-map=mondrian_map.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mondrian_map": ["*.yaml", "*.json"],
    },
    keywords="bioinformatics, pathway analysis, visualization, mondrian maps, streamlit",
    project_urls={
        "Bug Reports": "https://github.com/your-username/mondrian-map/issues",
        "Source": "https://github.com/your-username/mondrian-map",
        "Documentation": "https://github.com/your-username/mondrian-map/docs",
    },
) 