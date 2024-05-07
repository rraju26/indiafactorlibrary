from setuptools import setup, find_packages

setup(
    name="IndiaFactorLibrary",
    version="0.1.0",
    description="A Python library to fetch and analyse Fama/French and other Factors data for Indian equities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "lxml"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    license='MIT',
)
