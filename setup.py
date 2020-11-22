from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="SqlAlchemy_Tools",
    version="0.0.1-b0",
    include_package_data=True,
    packages=find_packages(),

    install_requires=[
        'sqlalchemy',
        'sqlalchemy-repr',
        'pandas',
    ],

    author="Andy Everitt",
    author_email="andreweveritt@e3d-online.com",
    description="Wrapper to make using SqlAlchemy easier, thread safe, helper methods etc.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AndyEveritt/SqlAlchemyTools",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)