from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="SqlAlchemy_Tools",
    version="0.1.0-b4",
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "alembic==1.4.3",
        "arrow==0.17.0",
        "flask-wtf==0.14.3",
        "inflection==0.5.1",
        "manage.py==0.2.10",
        "pandas==1.1.4",
        "pymysql==0.10.1",
        "pg8000==1.16.6",
        "sqlalchemy==1.3.20",
        "sqlalchemy-repr==0.0.2",
        "wtforms_alchemy==0.17.0",
    ],

    author="Andy Everitt",
    author_email="andreweveritt@e3d-online.com",
    description="SqlAlchemyTools provides similar functionality to Flask-SqlAlchemy & Flask-Migrate without being dependant on Flask.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AndyEveritt/SqlAlchemyTools",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
