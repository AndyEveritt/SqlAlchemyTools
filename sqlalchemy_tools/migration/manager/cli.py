from __future__ import absolute_import

import os
import getpass
from glob import glob
import sys

try:
    raw_input
except NameError:
    raw_input = input

try:
    from collections import OrderedDict
except ImportError:
    from .packages.ordereddict import OrderedDict  # NOQA

__all__ = ('Args', )

STDOUT = sys.stdout.write
NEWLINES = ('\n', '\r', '\r\n')


class Args(object):
    """CLI Argument management."""

    def __init__(self, args=None, no_argv=False):
        if args is None:
            if not no_argv:
                self._args = sys.argv[1:]
            else:
                self._args = []
        else:
            self._args = args

    def __len__(self):
        return len(self._args)

    def __repr__(self):
        return '<args %s>' % (repr(self._args))

    def __getitem__(self, i):
        try:
            return self.all[i]
        except IndexError:
            return None

    def __contains__(self, x):
        return self.first(x) is not None

    def get(self, x):
        """Returns argument at given index, else none."""
        try:
            return self.all[x]
        except IndexError:
            return None

    def get_with(self, x):
        """Returns first argument that contains given string."""
        return self.all[self.first_with(x)]

    def remove(self, x):
        """Removes given arg (or list thereof) from Args object."""

        def _remove(x):
            found = self.first(x)
            if found is not None:
                self._args.pop(found)

        if is_collection(x):
            for item in x:
                _remove(x)
        else:
            _remove(x)

    def pop(self, x):
        """Removes and Returns value at given index, else none."""
        try:
            return self._args.pop(x)
        except IndexError:
            return None

    def any_contain(self, x):
        """Tests if given string is contained in any stored argument."""

        return bool(self.first_with(x))

    def contains(self, x):
        """Tests if given object is in arguments list.
           Accepts strings and lists of strings."""

        return self.__contains__(x)

    def first(self, x):
        """Returns first found index of given value (or list of values)"""

        def _find(x):
            try:
                return self.all.index(str(x))
            except ValueError:
                return None

        if is_collection(x):
            for item in x:
                found = _find(item)
                if found is not None:
                    return found
            return None
        else:
            return _find(x)

    def first_with(self, x):
        """Returns first found index containing value (or list of values)"""

        def _find(x):
            try:
                for arg in self.all:
                    if x in arg:
                        return self.all.index(arg)
            except ValueError:
                return None

        if is_collection(x):
            for item in x:
                found = _find(item)
                if found:
                    return found
            return None
        else:
            return _find(x)

    def first_without(self, x):
        """Returns first found index not containing value (or list of values).
        """

        def _find(x):
            try:
                for arg in self.all:
                    if x not in arg:
                        return self.all.index(arg)
            except ValueError:
                return None

        if is_collection(x):
            for item in x:
                found = _find(item)
                if found:
                    return found
            return None
        else:
            return _find(x)

    def start_with(self, x):
        """Returns all arguments beginning with given string (or list thereof).
        """

        _args = []

        for arg in self.all:
            if is_collection(x):
                for _x in x:
                    if arg.startswith(x):
                        _args.append(arg)
                        break
            else:
                if arg.startswith(x):
                    _args.append(arg)

        return Args(_args, no_argv=True)

    def contains_at(self, x, index):
        """Tests if given [list of] string is at given index."""

        try:
            if is_collection(x):
                for _x in x:
                    if (_x in self.all[index]) or (_x == self.all[index]):
                        return True
                    else:
                        return False
            else:
                return (x in self.all[index])

        except IndexError:
            return False

    def has(self, x):
        """Returns true if argument exists at given index.
           Accepts: integer.
        """

        try:
            self.all[x]
            return True
        except IndexError:
            return False

    def value_after(self, x):
        """Returns value of argument after given found argument
        (or list thereof).
        """

        try:
            try:
                i = self.all.index(x)
            except ValueError:
                return None

            return self.all[i + 1]

        except IndexError:
            return None

    @property
    def grouped(self):
        """Extracts --flag groups from argument list.
           Returns {format: Args, ...}
        """

        collection = OrderedDict(_=Args(no_argv=True))

        _current_group = None

        for arg in self.all:
            if arg.startswith('-'):
                _current_group = arg
                collection[arg] = Args(no_argv=True)
            else:
                if _current_group:
                    collection[_current_group]._args.append(arg)
                else:
                    collection['_']._args.append(arg)

        return collection

    @property
    def last(self):
        """Returns last argument."""

        try:
            return self.all[-1]
        except IndexError:
            return None

    @property
    def all(self):
        """Returns all arguments."""

        return self._args

    def all_with(self, x):
        """Returns all arguments containing given string (or list thereof)"""

        _args = []

        for arg in self.all:
            if is_collection(x):
                for _x in x:
                    if _x in arg:
                        _args.append(arg)
                        break
            else:
                if x in arg:
                    _args.append(arg)

        return Args(_args, no_argv=True)

    def all_without(self, x):
        """Returns all arguments not containing given string (or list thereof).
        """

        _args = []

        for arg in self.all:
            if is_collection(x):
                for _x in x:
                    if _x not in arg:
                        _args.append(arg)
                        break
            else:
                if x not in arg:
                    _args.append(arg)

        return Args(_args, no_argv=True)

    @property
    def flags(self):
        """Returns Arg object including only flagged arguments."""

        return self.start_with('-')

    @property
    def not_flags(self):
        """Returns Arg object excluding flagged arguments."""

        return self.all_without('-')

    @property
    def files(self, absolute=False):
        """Returns an expanded list of all valid paths that were passed in."""

        _paths = []

        for arg in self.all:
            for path in expand_path(arg):
                if os.path.exists(path):
                    if absolute:
                        _paths.append(os.path.abspath(path))
                    else:
                        _paths.append(path)

        return _paths

    @property
    def not_files(self):
        """Returns a list of all arguments that aren't files/globs."""

        _args = []

        for arg in self.all:
            if not len(expand_path(arg)):
                if not os.path.exists(arg):
                    _args.append(arg)

        return Args(_args, no_argv=True)

    @property
    def copy(self):
        """Returns a copy of Args object for temporary manipulation."""

        return Args(self.all)


def expand_path(path):
    """Expands directories and globs in given path."""

    paths = []
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if os.path.isdir(path):

        for (dir, dirs, files) in os.walk(path):
            for file in files:
                paths.append(os.path.join(dir, file))
    else:
        paths.extend(glob(path))

    return paths


def is_collection(obj):
    """Tests if an object is a collection. Strings don't count."""

    if isinstance(obj, basestring):
        return False

    return hasattr(obj, '__getitem__')


class Writer(object):
    """WriterUtilized by context managers."""

    shared = dict(indent_level=0, indent_strings=[])

    def __init__(self, indent=0, quote='', indent_char=' '):
        self.indent = indent
        self.indent_char = indent_char
        self.indent_quote = quote
        if self.indent > 0:
            self.indent_string = ''.join((
                str(quote),
                (self.indent_char * (indent - len(self.indent_quote)))
            ))
        else:
            self.indent_string = ''.join((
                ('\x08' * (-1 * (indent - len(self.indent_quote)))),
                str(quote))
            )

        if len(self.indent_string):
            self.shared['indent_strings'].append(self.indent_string)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.shared['indent_strings'].pop()

    def __call__(self, s, newline=True, stream=STDOUT):
        if newline:
            s = tsplit(s, NEWLINES)
            s = map(str, s)
            indent = ''.join(self.shared['indent_strings'])

            s = (str('\n' + indent)).join(s)

        _str = ''.join((
            ''.join(self.shared['indent_strings']),
            str(s),
            '\n' if newline else ''
        ))
        stream(_str)


def puts(s='', newline=True, stream=STDOUT):
    """Prints given string to stdout via Writer interface."""
    Writer()(s, newline, stream=stream)


def indent(indent=4, quote=''):
    """Indentation context manager."""
    return Writer(indent=indent, quote=quote)


def tsplit(string, delimiters):
    """Behaves str.split but supports tuples of delimiters."""

    delimiters = tuple(delimiters)
    stack = [string, ]

    for delimiter in delimiters:
        for i, substring in enumerate(stack):
            substack = substring.split(delimiter)
            stack.pop(i)
            for j, _substring in enumerate(substack):
                stack.insert(i + j, _substring)

    return stack


def min_width(string, cols, padding=' '):
    """Returns given string with right padding."""

    stack = tsplit(str(string), NEWLINES)

    for i, substring in enumerate(stack):
        _sub = substring.ljust((cols + 0), padding)
        stack[i] = _sub

    return '\n'.join(stack)


TRUE_CHOICES = ('y', 'yes')
FALSE_CHOICES = ('n', 'no')


def process_value(value, empty=False, type=str, default=None, allowed=None,
        true_choices=TRUE_CHOICES, false_choices=FALSE_CHOICES):
    """Process prompted value.

    :param str value: The value to process.
    :param bool empty: Allow empty value.
    :param type type: The expected type.
    :param mixed default: The default value.
    :param tuple allowed: The allowed values.
    :param tuple true_choices: The accpeted values for True.
    :param tuple false_choices: The accepted values for False.
    """
    if allowed is not None and value not in allowed:
        raise Exception('Invalid input')

    if type is bool:
        if value in true_choices:
            return True
        if value in false_choices:
            return False
    if value in ('', '\n'):
        if default is not None:
            return default
        if empty:
            return None
        raise Exception('Invalid input')

    return type(value)


def prompt(message, empty=False, hidden=False, type=str, default=None,
        allowed=None, true_choices=TRUE_CHOICES, false_choices=FALSE_CHOICES,
        max_attempt=3, confirm=False):
    """Prompt user for value.

    :param str message: The prompt message.
    :param bool empty: Allow empty value.
    :param bool hidden: Hide user input.
    :param type type: The expected type.
    :param mixed default: The default value.
    :param tuple allowed: The allowed values.
    :param tuple true_choices: The accpeted values for True.
    :param tuple false_choices: The accepted values for False.
    :param int max_attempt: How many times the user is prompted back in case
        of invalid input.
    :param bool confirm: Enforce confirmation.
    """
    from manager import Error

    if allowed is not None and empty:
        allowed = allowed + ('', '\n')

    if type is bool:
        allowed = true_choices + false_choices

    if allowed is not None:
        message = "%s [%s]" % (message, ", ".join(allowed))

    if default is not None:
        message = "%s (default: %s) " % (message, default)

    handler = raw_input
    if hidden:
        handler = getpass.getpass

    attempt = 0

    while attempt < max_attempt:
        try:
            value = process_value(
                handler("%s : " % message),
                empty=empty,
                type=type,
                default=default,
                allowed=allowed,
                true_choices=true_choices,
                false_choices=false_choices,
            )
            break
        except:
            attempt = attempt + 1

            if attempt == max_attempt:
                raise Error('Invalid input')

    if confirm:
        confirmation = prompt("%s (again)" % message, empty=empty,
            hidden=hidden, type=type, default=default, allowed=allowed,
            true_choices=true_choices, false_choices=false_choices,
            max_attempt=max_attempt)

        if value != confirmation:
            raise Error('Values do not match')

    return value


class Colored(object):
    def __init__(self, color, string):
        self.color = color
        self.string = string

    def __len__(self):
        return len(self.string)

    def __str__(self):
        if sys.stdout.isatty():
            return "%s%s\033[0m" % (self.color, self.string)
        return self.string

    def __eq__(self, other):
        return self.string == other


def blue(string):
    return Colored('\033[94m', string)


def green(string):
    return Colored('\033[92m', string)


def red(string):
    return Colored('\033[91m', string)
