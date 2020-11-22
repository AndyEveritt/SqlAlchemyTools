from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy_utils import Database
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint


db = Database()
Base = db.Base


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




db.create_all_metadata()
# db.register_models([User, Address])

u1 = User(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User(name='Dave', fullname='Dave Owen', nickname='Dav Machine')
db.save([u1, u2])

u3 = db.get_or_create(User, {'name': 'Simon'})
pass
