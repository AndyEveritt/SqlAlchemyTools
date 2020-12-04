# SqlAlchemyTools

SqlAlchemyTools is a tool that provides similar functionality to Flask_SqlAlchemy without being dependant on Flask.

# Installation

Install SqlAlchemyTools with pip:

```
pip install sqlalchemy-tools
```

# Features

- Database:
  - Just by instantiating with Database(), SqlAlchemyTools automatically creates the session, model and everything necessary for SQLAlchemy.
  - Works with & without a Flask app with minimal code change
  - Thread safe by using [`scoped_session`](https://docs.sqlalchemy.org/en/13/orm/contextual.html)
  - Integration with Pandas to allow quick dataframe insertion and retriving queries as dataframes
  - It provides easy methods such as query(), create(), update(), delete(), to select, create, update, delete entries respectively.
  - Autogenerate the `__tablename__` as the snake case equivalent on the model name if not explictly defined (not pluralised)
  - It uses Arrow for DateTime
  - DateTime is saved in UTC and uses the ArrowType from the SQLAlchemy-Utils
  - Added some data types: JSONType, EmailType, and the whole SQLAlchemy-Utils Type
  - db.now -> gives you the Arrow UTC type
  - Paginated results
  - Pretty object representation
  - It is still SQLAlchemy. You can access all the SQLAlchemy awesomeness
- Migration:
  - Inbuilt migration support similar to Flask-migrate
  - Create a `manage.py` file to easily migrate your database
- ModelFrom:
  - Quickly add all the fields of a model to a WTF form
  - Supports `include`, `exclude`, `only`

# Contents

- [SqlAlchemyTools](#sqlalchemytools)
- [Installation](#installation)
- [Features](#features)
- [Contents](#contents)
- [Quick Overview:](#quick-overview)
  - [Database](#database)
    - [Create the model](#create-the-model)
    - [Retrieve all records](#retrieve-all-records)
    - [Create new record](#create-new-record)
    - [Get a record by primary key (id)](#get-a-record-by-primary-key-id)
    - [Update record from primary key](#update-record-from-primary-key)
    - [Update record from query iteration](#update-record-from-query-iteration)
    - [Delete a record](#delete-a-record)
    - [Query with filter](#query-with-filter)
  - [Migration](#migration)
    - [Why use SqlAlchemyTools migration vs. Alembic directly](#why-use-sqlalchemytools-migration-vs-alembic-directly)
    - [Create `manage.py`](#create-managepy)
    - [Initialise migrations folder](#initialise-migrations-folder)
    - [Create a new migration](#create-a-new-migration)
    - [Upgrade database](#upgrade-database)
    - [Downgrade database](#downgrade-database)
    - [Help](#help)
  - [ModelForm](#modelform)
- [How to use](#how-to-use)

# Quick Overview:

## Database

### Create the model

```python
from sqlalchemy_tools import Database

db = Database('sqlite://')

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = db.Column(db.String(25))
    location = db.Column(db.String(50), default="USA")
    last_access = db.Column(db.Datetime)
```

### Retrieve all records

```python
User.query.all()
```

### Create new record

```python
user = User.create(name="Mardix", location="Moon")

# or

user = User(name="Mardix", location="Moon").save()
```

### Get a record by primary key (id)

```python
user = User.get(1234)
```

### Update record from primary key

```python
user = User.get(1234)
if user:
    user.update(location="Neptune")
```

### Update record from query iteration

```python
for user in User.query:
    user.update(last_access=db.utcnow())
```

### Delete a record

```python
user = User.get(1234)
if user:
    user.delete()
```

### Query with filter

```python
all = User.query.filter(User.location == "USA")

for user in users:
    ...
```

## Migration

SqlAlchemyTools handles SQLAlchemy database migrations using Alembic. The database operations are made available through a command-line interface.

### Why use SqlAlchemyTools migration vs. Alembic directly

SqlAlchemyTools configures Alembic in the proper way to work with your database whether it is with or without Flask. In terms of the actual database migrations, everything is handled by Alembic so you get exactly the same functionality.

### Create `manage.py`

To support database migrations, you need to create a `manage.py` file.

> The file can be called anything

```python
from sqlalchemy_tools.migration import Migrate, migrate_manager
from sqlalchemy_tools import Database


# create/import your database
db = Database('sqlite:///tmp.db')

# create a `migrate` object that is linked to your database
migrate = Migrate(db)
migrate_manager.set_migrate(migrate)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128))


if __name__ == '__main__':
    migrate_manager.main()
```

### Initialise migrations folder

The `migrations` folder need to be initialise which will contain your database versions:

```bash
python manage.py init
```

### Create a new migration

Whenever there is a change to the models that you want reflected in the database:

```bash
python manage.py migrate -m "Intial migration"
```

### Upgrade database

To upgrade the database to the latest migration:

```bash
python manage.py upgrade
```

### Downgrade database

To downgrade the database by 1 migration:

```bash
python manage.py downgrade
```

### Help

To see all the commands that are available run:

```bash
python manage.py --help
```

## ModelForm

Make a Flask compatible version of the [**WTForms-Alchemy**](https://wtforms-alchemy.readthedocs.io/en/latest/index.html) ModelForm

```python
from sqlalchemy_tools import create_model_form
from sqlalchemy_tools import Database

# create/import your database
db = Database('sqlite:///tmp.db')
ModelForm = create_model_form(db)

class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['last_access']
```

# How to use

Complete guides for the different modules can be found below:

- [Database](docs/database.md)
- [Migration](docs/migration.md)


