from six import string_types
from sqlalchemy import inspect
from sqlalchemy_mixins import InspectionMixin


class ReprMixin(InspectionMixin):
    __abstract__ = True
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @property
    def _id_str(self):
        if not self.primary_keys:
            return None
        pks = []
        for pk in self.primary_keys:
            value = self._repr_attr(pk)
            pks.append(f"{pk}={value}")

        return ', '.join(pks)

    def _repr_attr(self, attr):
        max_length = self.__repr_max_length__
        if not hasattr(self, attr):
            raise KeyError("{} has incorrect attribute '{}' in "
                           "__repr__attrs__".format(self.__class__, attr))
        value = getattr(self, attr)
        wrap_in_quote = isinstance(value, string_types)

        value = str(value)
        if len(value) > max_length:
            value = value[:max_length] + '...'

        if wrap_in_quote:
            value = f"'{value}'"

        return value

    @property
    def _repr_attrs_str(self):

        values = []
        if self.__repr_attrs__ == '__all__':
            self.__repr_attrs__ = [column for column in self.columns if column not in self.primary_keys]

        for key in self.__repr_attrs__:
            value = self._repr_attr(key)
            values.append(f"{key}={value}")

        return ', '.join(values)

    def __repr__(self):
        # get id like '#123'
        id_str = (self._id_str) if self._id_str else ''
        # join class name, id and repr_attrs
        repr_attrs = ', '+self._repr_attrs_str if self._repr_attrs_str else ''
        return f"<{self.__class__.__name__}({id_str}{repr_attrs})>"
