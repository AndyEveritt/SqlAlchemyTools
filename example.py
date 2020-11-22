from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
)
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
    addresses = relationship('Address', back_populates='user')


class Address(db.Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")




db.create_all_metadata()    # only required if not using alembic or using a database in memory
# db.register_models([User, Address])

u1 = User(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User(name='Dave', fullname='Dave Owen', nickname='Dav Machine')
db.save([u1, u2])

u3 = db.get_or_create(User, {'name': 'Simon'})
pass
