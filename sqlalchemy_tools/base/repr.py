from __future__ import unicode_literals

import io
import sys

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta

from reprlib import Repr as _Repr


__all__ = ['Repr', 'PrettyRepr', 'RepresentableBase',
           'PrettyRepresentableBase']


class Repr(_Repr):
    def repr(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return self.repr_Base(obj, self.maxlevel)
        if sys.version_info < (3,):
            return _Repr.repr(self, obj)
        else:
            return super(Repr, self).repr(obj)

    def repr_Base(self, obj, level):
        class_repr = self._repr_class(obj, level)
        attrs_repr = self._repr_attrs(obj, level)
        return f'{class_repr}({attrs_repr})'

    def _repr_class(self, obj, level):
        return obj.__class__.__name__

    def _repr_attrs(self, obj, level):
        represented_attrs = []
        for attr in self._iter_attrs(obj):
            represented_attr = self._repr_attr(attr, level)
            represented_attrs.append(represented_attr)
        return ', '.join(represented_attrs)

    def _repr_attr(self, obj, level):
        attr_name, attr_value = obj
        if hasattr(attr_value, 'isoformat'):
            return '%s=%r' % (attr_name, attr_value.isoformat())
        return '%s=%r' % (attr_name, attr_value)

    def _iter_attrs(self, obj):
        attr_names = inspect(obj.__class__).columns.keys()
        for attr_name in attr_names:
            yield (attr_name, getattr(obj, attr_name))


class PrettyRepr(Repr):
    def __init__(self, *args, **kwargs):
        indent = kwargs.pop('indent', None)
        if indent is None:
            self.indent = ' ' * 4
        else:
            self.indent = indent
        if sys.version_info < (3,):
            Repr.__init__(self, *args, **kwargs)
        else:
            super(PrettyRepr, self).__init__(*args, **kwargs)

    def repr_Base(self, obj, level):
        output = io.StringIO()
        output.write('<%s' % self._repr_class(obj, level))
        is_first_attr = True
        for attr in self._iter_attrs(obj):
            if not is_first_attr:
                output.write(',')
            is_first_attr = False
            represented_attr = self._repr_attr(attr, level)
            output.write('\n' + self.indent + represented_attr)
        output.write('>')
        return output.getvalue()


_shared_repr = Repr()
_shared_pretty_repr = PrettyRepr()


class RepresentableBase(object):
    def __repr__(self):
        return _shared_repr.repr(self)


class PrettyRepresentableBase(object):
    def __repr__(self):
        return _shared_pretty_repr.repr(self)
