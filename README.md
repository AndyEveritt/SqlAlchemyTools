# SqlAlchemy-Tools
SqlAlchemy_Tools is a tool that provides similar functionality to Flask_SqlAlchemy without being dependant on Flask.

# Installation
Install SqlAlchemy-Tools with pip:
```
pip install sqlalchemy-tools
```

# Features
* Thread safe by using [`scoped_session`](https://docs.sqlalchemy.org/en/13/orm/contextual.html)
* Integration with Pandas to allow quick dataframe insertion and retriving queries as dataframes
* GetOrCreate functionality
* Checking if an object is valid
* Other general helper methods for creating/getting information

# Example
```python
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy import (Column, String, Integer, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy_tools import Database

db = Database('sqlite:///tmp.db')


class User(db.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


db.create_all_metadata()    # only required if not using alembic or using a database in memory
# db.register_models([User, Address])   # optional to allow for single imports, allows models to be accessed as `db.User`

u1 = User(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User(name='Dave', fullname='Dave Owen', nickname='Dav Machine')
db.save([u1, u2])

u3 = db.get_or_create(User, {'name': 'Simon'})
```