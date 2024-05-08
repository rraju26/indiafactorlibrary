from setuptools import setup, find_packages

setup(
    name="indiafactorlibrary",
    version="0.0.4",
    description="A Python library to fetch data from Invespar Factor library for Indian equities.",
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
    license='Apache License 2.0',
)
