import argparse
from functools import wraps
import logging
import os
import sys
from flask import current_app
from manager import Manager
from alembic import __version__ as __alembic_version__
from alembic.config import Config as AlembicConfig
from alembic import command
from alembic.util import CommandError

alembic_version = tuple([int(v) for v in __alembic_version__.split('.')[0:3]])
log = logging.getLogger(__name__)


class _MigrateConfig(object):
    def __init__(self, migrate, db, **kwargs):
        self.migrate: Migrate = migrate
        self.db = db
        self.directory = migrate.directory
        self.configure_args = kwargs

    @property
    def metadata(self):
        """
        Backwards compatibility, in old releases app.extensions['migrate']
        was set to db, and env.py accessed app.extensions['migrate'].metadata
        """
        return self.db.metadata


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


class Migrate(object):
    def __init__(self, db, app=None, directory='migrations', **kwargs):
        self.configure_callbacks = []
        self.db = db
        self.directory = str(directory)
        self.alembic_ctx_kwargs = kwargs
        self.config = _MigrateConfig(
            self, self.db, **self.alembic_ctx_kwargs)
        if app is not None and db is not None:
            self.init_app(app, db, directory)

    def init_app(self, app, db=None, directory=None, **kwargs):
        self.db = db or self.db
        self.directory = str(directory or self.directory)
        self.alembic_ctx_kwargs.update(kwargs)
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['migrate'] = self.config

    def configure(self, f):
        self.configure_callbacks.append(f)
        return f

    def call_configure_callbacks(self, config):
        for f in self.configure_callbacks:
            config = f(config)
        return config

    def get_config(self, directory=None, x_arg=None, opts=None):
        if directory is None:
            directory = self.directory
        directory = str(directory)
        config = Config(os.path.join(directory, 'alembic.ini'))
        config.set_main_option('script_location', directory)
        if config.cmd_opts is None:
            config.cmd_opts = argparse.Namespace()
        for opt in opts or []:
            setattr(config.cmd_opts, opt, True)
        if not hasattr(config.cmd_opts, 'x'):
            if x_arg is not None:
                setattr(config.cmd_opts, 'x', [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, 'x', None)
        return self.call_configure_callbacks(config)


def catch_errors(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (CommandError, RuntimeError) as exc:
            log.error('Error: ' + str(exc))
            sys.exit(1)
    return wrapped


def get_next_rev_id(directory):
    count = 0
    for filename in os.listdir(directory):
        if not filename.endswith('.py'):
            continue
        count += 1
    return str(count + 1).zfill(4)


class MigrateManager(Manager):
    @property
    def migrate_config(self):
        migrate_config = getattr(self, '_migrate_config', None)
        if not migrate_config:
            raise ValueError("'migrate_config' not set")
        return self._migrate_config

    @migrate_config.setter
    def migrate_config(self, value: _MigrateConfig):
        if isinstance(value, _MigrateConfig):
            self._migrate_config = value
            return self.migrate_config

    def set_migrate(self, migrate: Migrate):
        self.migrate_config = migrate.config


migrate_manager = MigrateManager()


@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.arg('template', flag='template', default='default',
                     help=("Multiple databases migraton (default is False)"))
@migrate_manager.command
@catch_errors
def init(directory=None, template=None):
    """Creates a new migration repository"""
    if directory is None:
        directory = migrate_manager.migrate_config.directory
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    config = migrate_manager.migrate_config.migrate.call_configure_callbacks(config)
    if not os.path.exists(os.path.join(config.get_template_directory(), template)):
        raise ValueError("Template does not exist")
    command.init(config, directory, template)


@migrate_manager.arg('rev_id', flag='rev-id', default=None,
                     help=('Specify a hardcoded revision id instead of generating the next one in sequence'))
@migrate_manager.arg('version_path', flag='version-path', default=None,
                     help=('Specify specific path from config for version file'))
@migrate_manager.arg('branch_label', flag='branch-label', default=None,
                     help=('Specify a branch label to apply to the new revision'))
@migrate_manager.arg('splice', flag='splice', type=bool,
                     default=False,
                     help=('Allow a non-head revision as the "head" to splice onto'))
@migrate_manager.arg('head', flag='head', default='head',
                     help=('Specify head revision or <branchname>@head to base new revision on'))
@migrate_manager.arg('sql', flag='sql', type=bool, default=False,
                     help=("Don't emit SQL to database - dump to standard output instead"))
@migrate_manager.arg('autogenerate', flag='autogenerate',
                     type=bool, default=False,
                     help=('Populate revision script with candidate '
                           'migration operations, based on comparison of '
                           'database to model'))
@migrate_manager.arg('message', flag='message', shortcut='m', default=None,
                     help='Revision message')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def revision(directory=None, message=None, autogenerate=False, sql=False,
             head='head', splice=False, branch_label=None, version_path=None,
             rev_id=None):
    """Create a new revision file."""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    if directory is None:
        directory = migrate_manager.migrate_config.directory
    if rev_id is None:
        rev_id = get_next_rev_id(os.path.join(directory, 'versions'))
    command.revision(config, message, autogenerate=autogenerate, sql=sql,
                     head=head, splice=splice, branch_label=branch_label,
                     version_path=version_path, rev_id=rev_id)


@migrate_manager.arg('rev_id', flag='rev-id', default=None,
                     help=('Specify a hardcoded revision id instead of generating the next one in sequence'))
@migrate_manager.arg('version_path', flag='version-path', default=None,
                     help=('Specify specific path from config for version file'))
@migrate_manager.arg('branch_label', flag='branch-label', default=None,
                     help=('Specify a branch label to apply to the new revision'))
@migrate_manager.arg('splice', flag='splice', type=bool,
                     default=False,
                     help=('Allow a non-head revision as the "head" to splice onto'))
@migrate_manager.arg('head', flag='head', default='head',
                     help=('Specify head revision or <branchname>@head to base new revision on'))
@migrate_manager.arg('sql', flag='sql', type=bool, default=False,
                     help=("Don't emit SQL to database - dump to standard output instead"))
@migrate_manager.arg('message', flag='message', shortcut='m', default=None,
                     help='Revision message')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.arg('x_arg', flag='x-arg', shortcut='x', default=None,
                     action='append', help=("Additional arguments consumed "
                                            "by custom env.py scripts"))
@migrate_manager.command
@catch_errors
def migrate(directory=None, message=None, sql=False, head='head', splice=False,
            branch_label=None, version_path=None, rev_id=None, x_arg=None):
    """Alias for 'revision --autogenerate'"""
    config = migrate_manager.migrate_config.migrate.get_config(
        directory, opts=['autogenerate'], x_arg=x_arg)
    if directory is None:
        directory = migrate_manager.migrate_config.directory
    if rev_id is None:
        rev_id = get_next_rev_id(os.path.join(directory, 'versions'))
    command.revision(config, message, autogenerate=True, sql=sql,
                     head=head, splice=splice, branch_label=branch_label,
                     version_path=version_path, rev_id=rev_id)


@migrate_manager.arg('revision', nargs='?', default='head',
                     help="revision identifier")
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def edit(directory=None, revision='current'):
    """Edit current revision."""
    if alembic_version >= (0, 8, 0):
        config = migrate_manager.migrate_config.migrate.get_config(
            directory)
        command.edit(config, revision)
    else:
        raise RuntimeError('Alembic 0.8.0 or greater is required')


@migrate_manager.arg('rev_id', flag='rev-id', default=None,
                     help=('Specify a hardcoded revision id instead of generating one'))
@migrate_manager.arg('branch_label', flag='branch-label', default=None,
                     help=('Specify a branch label to apply to the new revision'))
@migrate_manager.arg('message', flag='message', shortcut='m', default=None,
                     help='Revision message')
@migrate_manager.arg('revisions', nargs='+',
                     help='one or more revisions, or "heads" for all heads')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def merge(directory=None, revisions='', message=None, branch_label=None,
          rev_id=None):
    """Merge two revisions together.  Creates a new migration file"""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.merge(config, revisions, message=message,
                  branch_label=branch_label, rev_id=rev_id)


@migrate_manager.arg('tag', flag='tag', default=None,
                     help=("Arbitrary 'tag' name - can be used by custom env.py scripts"))
@migrate_manager.arg('sql', flag='sql', type=bool, default=False,
                     help=("Don't emit SQL to database - dump to standard output instead"))
@migrate_manager.arg('revision', nargs='?', default='head',
                     help="revision identifier")
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.arg('x_arg', flag='x-arg', shortcut='x', default=None,
                     action='append', help=("Additional arguments consumed "
                                            "by custom env.py scripts"))
@migrate_manager.command
@catch_errors
def upgrade(directory=None, revision='head', sql=False, tag=None, x_arg=None):
    """Upgrade to a later version"""
    config = migrate_manager.migrate_config.migrate.get_config(directory,
                                                               x_arg=x_arg)
    command.upgrade(config, revision, sql=sql, tag=tag)


@migrate_manager.arg('tag', flag='tag', default=None,
                     help=("Arbitrary 'tag' name - can be used by custom env.py scripts"))
@migrate_manager.arg('sql', flag='sql', type=bool, default=False,
                     help=("Don't emit SQL to database - dump to standard output instead"))
@migrate_manager.arg('revision', nargs='?', default="-1",
                     help="revision identifier")
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.arg('x_arg', flag='x-arg', shortcut='x', default=None,
                     action='append', help=("Additional arguments consumed "
                                            "by custom env.py scripts"))
@migrate_manager.command
@catch_errors
def downgrade(directory=None, revision='-1', sql=False, tag=None, x_arg=None):
    """Revert to a previous version"""
    config = migrate_manager.migrate_config.migrate.get_config(directory,
                                                               x_arg=x_arg)
    if sql and revision == '-1':
        revision = 'head:-1'
    command.downgrade(config, revision, sql=sql, tag=tag)


@migrate_manager.arg('revision', nargs='?', default="head",
                     help="revision identifier")
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def show(directory=None, revision='head'):
    """Show the revision denoted by the given symbol."""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.show(config, revision)


@migrate_manager.arg('indicate_current', flag='indicate-current', shortcut='i',
                     type=bool, default=False,
                     help=('Indicate current version (Alembic 0.9.9 or greater is required)'))
@migrate_manager.arg('verbose', flag='verbose', shortcut='v', type=bool,
                     default=False, help='Use more verbose output')
@migrate_manager.arg('rev_range', flag='rev-range', shortcut='r', default=None,
                     help=('Specify a revision range; format is [start]:[end]'))
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def history(directory=None, rev_range=None, verbose=False,
            indicate_current=False):
    """List changeset scripts in chronological order."""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    if alembic_version >= (0, 9, 9):
        command.history(config, rev_range, verbose=verbose,
                        indicate_current=indicate_current)
    else:
        command.history(config, rev_range, verbose=verbose)


@migrate_manager.arg('resolve_dependencies', flag='resolve-dependencies', type=bool,
                     default=False, help='Treat dependency versions as down revisions')
@migrate_manager.arg('verbose', flag='verbose', shortcut='v', type=bool,
                     default=False, help='Use more verbose output')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def heads(directory=None, verbose=False, resolve_dependencies=False):
    """Show current available heads in the script directory"""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.heads(config, verbose=verbose,
                  resolve_dependencies=resolve_dependencies)


@migrate_manager.arg('verbose', flag='verbose', shortcut='v', type=bool,
                     default=False, help='Use more verbose output')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def branches(directory=None, verbose=False):
    """Show current branch points"""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.branches(config, verbose=verbose)


@migrate_manager.arg('head_only', flag='head-only', type=bool,
                     default=False,
                     help='Deprecated. Use --verbose for additional output')
@migrate_manager.arg('verbose', flag='verbose', shortcut='v', type=bool,
                     default=False, help='Use more verbose output')
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def current(directory=None, verbose=False, head_only=False):
    """Display the current revision for each database."""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.current(config, verbose=verbose, head_only=head_only)


@migrate_manager.arg('tag', flag='tag', default=None,
                     help=("Arbitrary 'tag' name - can be used by custom env.py scripts"))
@migrate_manager.arg('sql', flag='sql', type=bool, default=False,
                     help=("Don't emit SQL to database - dump to standard output instead"))
@migrate_manager.arg('revision', default=None, help="revision identifier")
@migrate_manager.arg('directory', flag='directory', shortcut='d', default=None,
                     help=("Migration script directory (default is 'migrations')"))
@migrate_manager.command
@catch_errors
def stamp(directory=None, revision='head', sql=False, tag=None):
    """'stamp' the revision table with the given revision; don't run any
    migrations"""
    config = migrate_manager.migrate_config.migrate.get_config(directory)
    command.stamp(config, revision, sql=sql, tag=tag)
