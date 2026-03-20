from setuptools import setup, find_packages

version_ns = {}
with open("indiafactorlibrary/version.py") as version_file:
    exec(version_file.read(), version_ns)

setup(
    name="indiafactorlibrary",
    version=version_ns["__version__"],
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
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    license="Apache License 2.0",
)
