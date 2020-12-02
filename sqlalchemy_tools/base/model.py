import datetime
import json
import logging
import os
import threading
from typing import Any, Dict, List

import arrow
import inflection
import pandas as pd
import sqlalchemy
import sqlalchemy_utils as sa_utils
from arrow import utcnow
from sqlalchemy import *
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, make_transient, scoped_session, sessionmaker
from sqlalchemy.orm.exc import (MultipleResultsFound, NoResultFound,
                                UnmappedClassError)
from sqlalchemy.schema import MetaData

from .repr import RepresentableBase


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


class BaseModel(RepresentableBase):
    """
    Baseclass for custom user models.
    """
    __tablename__ = ModelTableNameDescriptor()
    __primary_key__ = "id"  # String

    def __iter__(self):
        """Returns an iterable that supports .next()
        so we can do dict(sa_instance).
        """
        for k in self.__dict__.keys():
            if not k.startswith('_'):
                yield (k, getattr(self, k))

    def to_dict(self):
        """
        Return an entity as dict
        :returns dict:
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
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
        return cls._query(cls).filter(getattr(cls, cls.__primary_key__) == pk).first()

    @classmethod
    def create(cls, **kwargs):
        """
        To create a new record
        :returns object: The new record
        """
        record = cls(**kwargs).save()
        return record

    def update(self, **kwargs):
        """
        Update an entry
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
        return self

    @classmethod
    def query(cls, *args):
        """
        :returns query:
        """
        if not args:
            query = cls._query(cls)
        else:
            query = cls._query(*args)
        return query

    def save(self):
        """
        Shortcut to add and save + rollback
        """
        try:
            self.db.add(self)
            self.db.commit()
            return self
        except Exception as e:
            self.db.rollback()
            raise

    def delete(self, *args, **kwargs):
        """
        Delete a record
        """
        try:
            self.db.session.delete(self)
            return self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise


class Model(BaseModel):
    """
    Model create
    """
    id = Column(Integer, primary_key=True)
    created_at = Column(sa_utils.ArrowType, default=utcnow)
    updated_at = Column(sa_utils.ArrowType, default=utcnow, onupdate=utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(sa_utils.ArrowType, default=None)

    @classmethod
    def query(cls, *args, **kwargs):
        """
        :returns query:
        :**kwargs:
            - include_deleted bool: True To filter in deleted records.
                                    By default it is set to False
        """
        if not args:
            query = cls._query(cls)
        else:
            query = cls._query(*args)

        if "include_deleted" not in kwargs or kwargs["include_deleted"] is False:
            query = query.filter(cls.is_deleted is not True)

        return query

    @classmethod
    def get(cls, id, include_deleted=False):
        """
        Select entry by id
        :param id: The id of the entry
        :param include_deleted: It should not query deleted record. Set to True to get all
        """
        return cls.query(include_deleted=include_deleted)\
                  .filter(cls.id == id)\
                  .first()

    def delete(self, delete=True, hard_delete=False):
        """
        Soft delete a record
        :param delete: Bool - To soft-delete/soft-undelete a record
        :param hard_delete: Bool - If true it will completely delete the record
        """
        # Hard delete
        if hard_delete:
            try:
                self.db.session.delete(self)
                return self.db.commit()
            except:
                self.db.rollback()
                raise
        else:
            data = {
                "is_deleted": delete,
                "deleted_at": utcnow() if delete else None
            }
            self.update(**data)
        return self
