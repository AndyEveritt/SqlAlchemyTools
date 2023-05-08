from setuptools import find_packages, setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="SqlAlchemy_Tools",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "alembic>=1.5.4",
        "arrow>=0.17.0",
        "flask-wtf>=0.14.3",
        "flask-validator>=1.4.2",
        "inflection>=0.5.1",
        "graphviz>=0.16",
        "manage.py>=0.2.10",
        "pandas>=1.2.2",
        "pymysql>=1.0.2",
        "pg8000>=1.17.0",
        "sadisplay>=0.4.9",
        "sqlalchemy>=1.3.23,<=1.4.48",
        "sqlalchemy-mixins>=1.2.1,<=1.5.3",
        "sqlalchemy-repr>=0.0.2",
        "wtforms_alchemy>=0.17.0",
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
