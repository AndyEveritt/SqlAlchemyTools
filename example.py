from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy_utils import Database, Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    addresses = relationship('Address', back_populates='user')


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")


db = Database()
db.register_models([User, Address])
db.initialise(temp_db=True)

u1 = User(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User(name='Dave', fullname='Dave Owen', nickname='Dav Machine')
db.save([u1, u2])

u3 = db.get_or_create(db.User, {'name': 'Simon'})
