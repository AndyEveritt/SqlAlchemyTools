from enum import unique
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy_tools import Database


# db = Database('sqlite:///tmp.db')
db = Database('sqlite://')


class User(db.Model):
    __tablename__ = 'users'
    __repr_attrs__ = '__all__'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String, unique=True)
    nickname = Column(String)
    addresses = relationship('Address', back_populates='user')


class Address(db.Model):
    __tablename__ = 'addresses'
    __repr_attrs__ = '__all__'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")


db.create_all()    # only required if not using alembic or using a database in memory

u1 = User.create(name='Dave', fullname='Dave Smith', nickname='Davo')
u2 = User.create(name='Dave', fullname='Dave Owen', nickname='Dav Machine')

User.bulk_insert([{'name': 'Andy'}, {'name': "Sam"}])
User(name='Dave', fullname='Dave Owen2', nickname=1).is_valid()

df = db.get_dataframe(User.query)
df.pop('id')


users = User.query.paginate(page=2, per_page=2)
print(list(users))
User.insert_dataframe(df)

User.get(1)
q = User.query()

u3 = db.get_or_create(User, {'name': 'Simon'})
User.query.all()
pass
