import datetime
import json
from typing import Any, Dict, List

import arrow
import inflection
import pandas as pd
from sqlalchemy.orm.query import Query
import sqlalchemy_utils as sa_utils
from sqlalchemy import *
from sqlalchemy_mixins import SerializeMixin, SmartQueryMixin
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .repr import ReprMixin
from .query import BaseQuery


class ModelTableNameDescriptor:
    """
    Create the table name if it doesn't exist.
    """

    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            tablename = inflection.underscore(type.__name__)
            setattr(type, '__tablename__', tablename)
        return tablename


class BaseModel(ReprMixin, SerializeMixin, SmartQueryMixin):
    """
    Baseclass for custom user models.
    """
    __abstract__ = True
    __tablename__ = ModelTableNameDescriptor()
    __primary_key__ = "id"  # String
    query: BaseQuery

    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))

    def to_json(self) -> str:
        """
        Convert the entity to JSON
        :returns str:
        """
        data = {}
        for k, v in self.to_dict().items():
            if isinstance(v, (datetime.datetime, sa_utils.ArrowType, arrow.Arrow)):
                v = v.isoformat()
            data[k] = v
        return json.dumps(data)

    @classmethod
    def get(cls, pk):
        """
        Select entry by its primary key. It must be define as
        __primary_key__ (string)
        """
        return cls.query.filter(getattr(cls, cls.__primary_key__) == pk).first()

    @classmethod
    def create(cls, **kwargs):
        """
        To create a new record
        :returns object: The new record
        """
        record = cls(**kwargs).save()
        return record

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        Filter class by kwargs, if no matching instance found, instance will be created.
        If ONE instance is found, it will be returned.
        If multiple instances found, raise MultipleResultsFound
        """
        query = cls.query.filter_by(**kwargs)
        try:
            result = query.one()
        except NoResultFound:
            result = cls.create(**kwargs)
        except MultipleResultsFound:
            raise

        return result

    def update(self, **kwargs):
        """
        Update an entry
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
        return self

    def save(self):
        """
        Shortcut to add and commit + rollback
        """
        try:
            with self.db.session.begin_nested():
                self.db.add(self)
        except Exception as e:
            raise
        self.db.commit()
        return self

    def delete(self):
        """
        Delete a record
        """
        try:
            with self.db.session.begin_nested():
                self.db.session.delete(self)
        except Exception as e:
            raise
        return self.db.commit()

    def is_valid(self) -> bool:
        """ Takes an sqlalchemy orm object and will return True if it is valid """
        if not self._sa_instance_state.transient:
            raise ValueError("Can not validate existing objects")

        # check to see if obj already exists in database as logic is not able to validate existing entries
        pk = getattr(self, self.__primary_key__)
        if self.get(pk) is not None:
            raise ValueError("Can not validate existing objects")

        save = self.db.session.begin_nested()
        dummy = self.db.session.begin_nested()
        try:
            dummy.session.add(self)
            dummy.commit()   # will raise IntegrityError if not valid

            # tidy up database
            save.rollback()

            # make obj useable again
            setattr(self, self.__primary_key__, None)
            return True
        except Exception as e:
            # make db.session useable again
            save.rollback()
            return False

    @classmethod
    def bulk_insert(cls, mappings: List[Dict], **kwargs):
        """
        Insert a list of dicts to the database.

        Not as fast as `insert_dataframe()` but can be faster than converting list to DataFrame then inserting
        """
        try:
            with cls.db.session.begin_nested():
                cls.db.session.session.bulk_insert_mappings(cls, mappings, **kwargs)
            cls.db.session.commit()
            return True
        except Exception as e:
            raise e

    @classmethod
    def insert_dataframe(cls, df: pd.DataFrame):
        """ Insert a Pandas dataframe into the database (fast) """
        save = cls.db.session.begin_nested()
        try:
            df.to_sql(cls.__tablename__, con=cls.db.engine, if_exists='append', index=False)
            return True
        except Exception as e:
            save.rollback()
            raise e
