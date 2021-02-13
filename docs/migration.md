[README](../README.md)

## Migration

- [Migration](#migration)
  - [Setup](#setup)
  - [Usage](#usage)
    - [help](#help)
    - [init](#init)
    - [revision](#revision)
    - [migrate](#migrate)
    - [edit](#edit)
    - [upgrade](#upgrade)
    - [downgrade](#downgrade)
    - [stamp](#stamp)
    - [current](#current)
    - [history](#history)
    - [show](#show)
    - [merge](#merge)
    - [heads](#heads)
    - [branches](#branches)
  - [Alter Sqlite](#alter-sqlite)
    - [Complications](#complications)
  - [Configuration Callbacks](#configuration-callbacks)

### Setup

SqlAlchemyTools exposes `Migrate` and `migrate_manager`

The `Migrate` class links the database and other configuration. The `migrate_manager` object contains all the cli functions

```python
from sqlalchemy_tools.migration import Migrate, migrate_manager

# create/import your database
from my_database_module import db

# create a `migrate` object that is linked to your database
migrate = Migrate(db)


if __name__ == '__main__':
    migrate_manager.main()
```

### Usage

After the extension is initialized, the command-line options will be available with several sub-commands through the `manage.py` type script created. Below is a list of the available sub-commands:

#### help

```
  python manage.py --help
```

Shows a list of available commands.

#### init

Initializes migration support for the application. The optional --multidb enables migrations for multiple databases configured as Flask-SQLAlchemy binds.

```
  python manage.py init [--multidb]
```

#### revision

Creates an empty revision script. The script needs to be edited manually with the upgrade and downgrade changes. See Alembic’s documentation for instructions on how to write migration scripts. An optional migration message can be included.

```
python manage.py revision [--message MESSAGE] [--autogenerate] [--sql] [--head HEAD] [--splice] [--branch-label BRANCH_LABEL] [--version-path VERSION_PATH] [--rev-id REV_ID]
```

#### migrate

Equivalent to revision --autogenerate. The migration script is populated with changes detected automatically. The generated script should to be reviewed and edited as not all types of changes can be detected automatically. This command does not make any changes to the database, just creates the revision script.

```
python manage.py migrate [--message MESSAGE] [--sql] [--head HEAD] [--splice] [--branch-label BRANCH_LABEL] [--version-path VERSION_PATH] [--rev-id REV_ID]
```

#### edit

Edit a revision script using $EDITOR.

```
python manage.py edit <revision>
```

#### upgrade

Upgrades the database. If revision isn’t given then "head" is assumed.

```
python manage.py upgrade [--sql] [--tag TAG] [--x-arg ARG] <revision>
```

#### downgrade

Downgrades the database. If revision isn’t given then -1 is assumed.

```
python manage.py downgrade [--sql] [--tag TAG] [--x-arg ARG] <revision>
```

#### stamp

Sets the revision in the database to the one given as an argument, without performing any migrations.

```
python manage.py stamp [--sql] [--tag TAG] <revision>
```

#### current

Shows the current revision of the database.

```
python manage.py current [--verbose]
```

#### history

Shows the list of migrations. If a range isn’t given then the entire history is shown.

```
python manage.py history [--rev-range REV_RANGE] [--verbose]
```

#### show

Show the revision denoted by the given symbol.

```
python manage.py show <revision>
```

#### merge

Merge two revisions together. Creates a new revision file.

```
python manage.py merge [--message MESSAGE] [--branch-label BRANCH_LABEL] [--rev-id REV_ID] <revisions>
```

#### heads

Show current available heads in the revision script directory.

```
python manage.py heads [--verbose] [--resolve-dependencies]
```

#### branches

Show current branch points.

```
python manage.py branches [--verbose]
```

Notes:

- All commands also take a --directory DIRECTORY option that points to the directory containing the migration scripts. If this argument is omitted the directory used is migrations.
- The default directory can also be specified as a directory argument to the Migrate constructor.
- The --sql option present in several commands performs an ‘offline’ mode migration. Instead of executing the database commands the SQL statements that need to be executed are printed to the console.
- Detailed documentation on these commands can be found in the Alembic’s command reference page.

### Alter Sqlite

Sqlite does not support altering columns. A work around is to use `render_as_batch=True` when initialising the `Migrate` object.

```python
from sqlalchemy_tools.migration import Migrate, migrate_manager

# create/import your database
from my_database_module import db

# create a `migrate` object that is linked to your database
migrate = Migrate(db, render_as_batch=True)
```

#### Complications

There are situations where batch mode alone does not solve upgrade errors.

A nasty type of issue occurs when the `ALTER TABLE` error occurs in the middle of a migration, after some operations were already applied. This could leave the database in an inconsistent state, where some changes from the migration script have been applied, but because of the error, the version is still pointing to the previous migration.

To unblock a database after a partial migration was applied, follow these steps:

- Determine which of the operations were applied
- Delete everything from the `upgrade()` function
- Edit the `downgrade()` function so that it only contains the reverse of the operations that were applied to your database
- Run `python manage.py upgrade`. This is going to update the database version
- Run `python manage.py downgrade`
- Delete the migration script and try again with batch mode enabled

Another common issue occurs when your table has unnamed constraints, which the batch mode process can't delete or modify because there is no way to refer to them by name. The Alembic documentation has some information on how to deal with unnamed constraints when using batch mode.

### Configuration Callbacks

Sometimes applications need to dynamically insert their own settings into the Alembic configuration. A function decorated with the configure callback will be invoked after the configuration is read, and before it is used. The function can modify the configuration object, or replace it with a different one.

```python
@migrate.configure
def configure_alembic(config):
    # modify config object
    return config
```

Multiple configuration callbacks can be defined simply by decorating multiple functions. The order in which multiple callbacks are invoked is undetermined.