from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="sqlalchemy_utils",
    version="0.0.1",
    include_package_data=True,
    packages=find_packages(),

    install_requires=[
        "sqlalchemy >= 1.3.20",
        "sqlalchemy-repr >= 0.0.2",
        "pandas >= 1.1.4",
    ],

    author="Andy Everitt",
    author_email="andreweveritt@e3d-online.com",
    description="Wrapper to make using SqlAlchemy easier, threading, helper methods etc.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AndyEveritt/SqlAlchemyUtils",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)