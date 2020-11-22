import datetime
import os
from typing import Any, Dict, List

import pandas as pd
import sqlalchemy as db
import logging
from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Text, and_, func, or_)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, make_transient
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound, UnmappedClassError
from sqlalchemy_repr import RepresentableBase


class Database:
    def __init__(self, database_file='sqlite://', base_class=RepresentableBase):
        """
        Link sqlalchemy to a database
        """
        self.engine = db.create_engine(database_file)
        logging.info(f'Database engine: {self.engine}')

        self._sessionmaker = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self._sessionmaker)

        self.Base = base_class
        pass

    @property
    def Base(self):
        return self._Base
    
    @Base.setter
    def Base(self, base_class, **kwargs):
        Base = declarative_base(cls=base_class, **kwargs)
        Base.query = self.Session.query_property()
        self._Base = Base

    def create_all_metadata(self):
        """ Create table metadata. Must be called after tables are defined  """
        self.Base.metadata.create_all(self.engine)

    def register_model(self, model):
        """ (Not required) Add a single model to the database to allow for single imports """
        setattr(self, model.__name__, model)

    def register_models(self, models):
        """ Add list of models to the database. This must be done before running `initialise()` """
        for model in models:
            self.register_model(model)

    def create_new_session(self, **kwargs):
        """ Create a new session (database transaction) """
        self.Session.remove()
        self.Session = scoped_session(self._sessionmaker, **kwargs)
        return self.Session

    def save(self, data: List):
        """ Commit an array of objects to the database """
        try:
            iter(data)
        except TypeError:
            data = [data]

        for obj in data:
            self.Session.add(obj)
        self.Session.commit()

    def get_query(self, model, params: Dict = {}):
        """ Returns a query object that can be further filtered """
        return self.Session.query(model).filter_by(**params)

    def get_all(self, model, params: Dict = {}):
        """
        Return all results from a model. It will optionally filter based on a `params` dict.
        The keys of `params` must be the same as the column names to filter in the model.
        """
        query = self.get_query(model, params)
        results = query.all()

        return results

    def get_one(self, model, params: Dict = {}):
        """
        Return one results from a model. It will optionally filter based on a `params` dict.
        The keys of `params` must be the same as the column names to filter in the model.
        """
        query = self.get_query(model, params)
        results = query.one()

        return results

    def get_or_create(self, model, params: Dict):
        """
        Return a single result from a model that matches a `params` dict.
        The keys of `params` must be the same as the column names to filter in the model.
        If no matching object exists in the database then one will be created and returned.
        If multiple objects are returned by the query then an exception is raised (be more specific with `params`).
        """
        try:
            result = self.get_one(model, params)
        except NoResultFound:
            result = self.create(model, params)
        except MultipleResultsFound:
            raise MultipleResultsFound

        return result

    def create(self, model, params: Dict):
        """
        Creates a new object and commits to database.
        For efficiency it is recommended not to use this for bulk inserts
        """
        result = model(**params)
        try:
            self.save([result])
            return result
        except IntegrityError:
            raise

    def bulk_insert(self, model, mappings: List[Dict], **kwargs):
        """
        Insert a list of dicts to the database.
        
        Not as fast as `insert_dataframe()` but can be faster than converting list to DataFrame then inserting
        """
        return self.Session.bulk_insert_mappings(model, mappings, **kwargs)

    def get_dataframe(self, model: Base, params: Dict):
        query = self.get_query(model, params)
        return pd.read_sql(query.statement, query.session.bind)

    def insert_dataframe(self, model, df: pd.DataFrame):
        """ Insert a Pandas dataframe into the database (fast) """
        return df.to_sql(model.__tablename__, con=self.engine, if_exists='append', index=False)

    def merge_obj(self, obj):
        """ Returns the input obj after merging it into the current thread """
        return self.Session.merge(obj)
    
    def is_valid(self, obj, pk: str = 'id') -> bool:
        """ Takes an sqlalchemy orm object and will return True if it is valid """
        try:
            self.Session.add(obj)
            self.Session.commit()   # will raise IntegrityError if not valid

            # tidy up database
            self.Session.delete(obj)
            self.Session.commit()

            # make obj useable again
            make_transient(obj)
            setattr(obj, pk, None)
            return True
        except IntegrityError:
            # make Session useable again
            self.Session.rollback()
            return False

