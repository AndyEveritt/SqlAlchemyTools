from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy_tools import Database, ActiveAlchemy


# db = Database('sqlite:///tmp.db')
db = ActiveAlchemy('sqlite://')


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    addresses = relationship('Address', back_populates='user')


class Address(db.Model):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")


db.create_all()    # only required if not using alembic or using a database in memory

u1 = User.create(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User.create(name='Dave', fullname='Dave Owen', nickname='Dav Machine')

User.get(1)

u3 = db.get_or_create(User, {'name': 'Simon'})
User.query.all()
pass
