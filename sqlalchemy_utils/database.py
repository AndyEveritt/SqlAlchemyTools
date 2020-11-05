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
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy_repr import RepresentableBase


Base = declarative_base(cls=RepresentableBase)


class Database:
    def initialise(self, database_file='sqlite://', temp_db=False):
        """
        Link sqlalchemy to a database

        Note: The database engine can only be accessed in the thread that created it
        """
        if temp_db:
            # Creates a database in memory. It will disappear once Python stops
            os.remove('tmp.db') if os.path.exists('tmp.db') else None
            self.engine = db.create_engine('sqlite:///tmp.db')
            Base.metadata.create_all(self.engine)
        else:
            self.engine = db.create_engine(database_file)

        logging.info(f'Database engine: {self.engine}')

        self._sessionmaker = sessionmaker(bind=self.engine)

        self.Session = scoped_session(self._sessionmaker)

    def register_model(self, model: Base):
        setattr(self, model.__name__, model)

    def register_models(self, models: List[Base]):
        for model in models:
            self.register_model(model)

    def create_new_session(self):
        """ Create a new session (database transaction) """
        self.Session.remove()
        self.Session = self._sessionmaker()
        self.query = self.Session.query

    def save(self, data: List):
        """ Commit an array of objects to the database """
        try:
            iter(data)
        except TypeError:
            data = [data]

        for obj in data:
            self.Session.add(obj)
        self.Session.commit()

    def get_query(self, model: Base, params: Dict = {}):
        return self.Session.query(model).filter_by(**params)

    def get_all(self, model: Base, params: Dict = {}):
        """
        Return all results from a model. It will optionally filter based on a `params` dict.
        The keys of `params` must be the same as the column names to filter in the model.
        """
        query = self.get_query(model, params)
        results = query.all()

        return results

    def get_one(self, model: Base, params: Dict = {}):
        """
        Return one results from a model. It will optionally filter based on a `params` dict.
        The keys of `params` must be the same as the column names to filter in the model.
        """
        query = self.get_query(model, params)
        results = query.one()

        return results

    def get_or_create(self, model: Base, params: Dict):
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

    def create(self, model: Base, params: Dict):
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
        return self.Session.bulk_insert_mappings(model, mappings, **kwargs)

    def insert_dataframe(self, model, df: pd.DataFrame):
        return df.to_sql(model.__tablename__, con=self.engine, if_exists='append', index=False)

    def merge_obj(self, obj):
        return self.Session.merge(obj)
