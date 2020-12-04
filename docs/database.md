[README](../README.md)

## Database

- [Database](#database)
  - [Create a connection](#create-a-connection)
    - [Databases Drivers & DB Connection examples](#databases-drivers--db-connection-examples)
  - [Create a Model](#create-a-model)
- [Models: _db.Model_](#models-dbmodel)
  - [db.Model Methods Description](#dbmodel-methods-description)
    - [query](#query)
    - [get(id)](#getid)
    - [create(\*\*kwargs)](#createkwargs)
    - [update(\*\*kwargs)](#updatekwargs)
    - [delete()](#delete)
    - [save()](#save)
    - [to_dict()](#to_dict)
    - [to_json()](#to_json)
    - [is_valid()](#is_valid)
    - [bulk_insert(mapping: List[Dict], \*\*kwargs)](#bulk_insertmapping-listdict-kwargs)
    - [insert_dataframe(df: pd.DataFrame)](#insert_dataframedf-pddataframe)
  - [db Methods Description](#db-methods-description)
    - [init_app(app)](#init_appapp)
    - [engine](#engine)
    - [metadata](#metadata)
    - [query](#query-1)
    - [add(\*args, \*\*kwargs)](#addargs-kwargs)
    - [flush(\*args, \*\*kwargs)](#flushargs-kwargs)
    - [commit()](#commit)
    - [rollback()](#rollback)
    - [create_all()](#create_all)
    - [drop_all()](#drop_all)
    - [reflect(meta)](#reflectmeta)
    - [get_dataframe(query)](#get_dataframequery)
    - [Method Chaining](#method-chaining)
    - [Aggegated selects](#aggegated-selects)
- [With Web Application](#with-web-application)
  - [More examples](#more-examples)
    - [Many databases, one web app](#many-databases-one-web-app)
    - [Many web apps, one database](#many-web-apps-one-database)
- [Pagination](#pagination)

### Create a connection

The `Database` class is used to instantiate a SQLAlchemy connection to
a database.

```python
from sqlalchemy_tools import Database

db = Database(dialect+driver://username:password@host:port/database)
```

#### Databases Drivers & DB Connection examples

SqlAlchemyTools comes with a `PyMySQL` and `PG8000` as drivers for MySQL
and PostgreSQL respectively, because they are in pure Python. But you can use
other drivers for better performance. `SQLite` is already built in Python.

**SQLite:**

```python
from sqlalchemy_tools import Database

db = Database("sqlite://") # in memory

# or

db = Database("sqlite:///foo.db") # DB file
```

**PostgreSql:**

```python
from sqlalchemy_tools import Database

db = Database("postgresql+pg8000://user:password@host:port/dbname")
```

**PyMySQL:**

```python
from sqlalchemy_tools import Database

db = Database("mysql+pymysql://user:password@host:port/dbname")
```

---

SqlAlchemyTools also provides access to all the SQLAlchemy
functions from the `sqlalchemy` and `sqlalchemy.orm` modules.
So you can declare models like the following examples:

### Create a Model

To start, create a model class and extends it with db.Model

```python
# mymodel.py

from sqlalchemy_tools import Database

db = Database("sqlite://")

class MyModel(db.Model):
    name = db.Column(db.String(25))
    is_live = db.Column(db.Boolean, default=False)

# Put at the end of the model module to auto create all models
db.create_all()
```

- It does an automatic table naming (if no table name is already defined using the `__tablename__` property)
  by using the class name. So, for example, a `User` model gets a table named `user`, `TodoList` becomes `todo_list`
  The name will not be plurialized.

---

## Models: _db.Model_

**db.Model** extends your model with helpers that turn your model into an active record like model. But underneath, it still uses the `db.session`

`db.Model` by default assumes that your primary key is `id`, but it can be overwritten.

```python
class MyExistingModel(db.BaseModel):
    __tablename__ = "my_old_table"
    __primary_key__  = "my_pk_id"

    my_pk_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ...
```

**BaseModel**

The default `db.Model` uses `from sqlalchemy_tools import BaseModel`. It can be changed by using a different `base_cls` on initialising the database

```python
db = Database('sqlite://', base_cls=MyBaseModel)
```

The BaseModel `__repr__` is formatted as:
`ClassName(attr_name=attr_value, ...)`

**BaseQuery**

The default model query is `from sqlalchemy_tools import BaseQuery`. It can be changed by using a different `query_cls` on initialising the database

```python
db = Database('sqlite://', query_cls=MyBaseQuery)
```

---

### db.Model Methods Description

#### query

To start querying the DB and returns a `db.session.query` object to filter or apply more conditions.

```python
for user in User.query:
    print(user.login)
```

To use with filter...

```python
all = User
        .query
        .order_by(User.updated_at.desc())
        .filter(User.location == "Charlotte")
```

#### get(id)

Get one record by id.

```python
id = 1234
user = User.get(id)
print(user.id)
print(user.login)
```

#### create(\*\*kwargs)

To create/insert new record. Same as **init**, but just a shortcut to it.

```python
record = User.create(login='abc', passw_hash='hash', profile_id=123)
print (record.login) # -> abc
```

or you can use the **init** with save()

```python
record = User(login='abc', passw_hash='hash', profile_id=123).save()
print (record.login) # -> abc
```

or

```python
record = User(login='abc', passw_hash='hash', profile_id=123)
db.add(record)
db.commit()
print (record.login) # -> abc
```

#### update(\*\*kwargs)

Update an existing record

```python
record = User.get(124)
record.update(login='new_login')
print (record.login) # -> new_login
```

#### delete()

To delete a record completely

```python
record = User.get(124)
record.delete()
```

#### save()

A shortcut to `session.add` + `session.commit()`

```python
record = User.get(124)
record.login = "Another one"
record.save()
```

#### to_dict()

Returns the model instance as a dictionary

```python
record = User.get(1234)
record_dict = record.to_dict()
```

#### to_json()

Returns the model instance as a JSON formatted string

```python
record = User.get(1234)
record_json = record.to_json()
```

#### is_valid()

Check whether the model instance will pass the database validation.

A nested session is created and the object is committed, if the commit is successful then the session is rolledback and the method returns True, else the session is rollback and the method returns False

```python
user = User(login='abc', passw_hash='hash', profile_id=123)
user.is_valid()
```

#### bulk_insert(mapping: List[Dict], \*\*kwargs)

Insert a list of dictionarys to the database

```python
User.bulk_insert([{'name': 'Andy'},
                  {'name': "Sam"}])
```

#### insert_dataframe(df: pd.DataFrame)

Insert a Pandas dataframe into the database. Faster than `bulk_insert` if you already have you data in DataFrame format

```python
df = pd.DataFrame()
... # fill df with data. Set ForeignKeys as the appropriate id, ignore relationship fields
User.insert_dataframe(df)
```

---

### db Methods Description

#### init_app(app)

This callback can be used to initialize an application for the
use with this database setup. In a web application or a multithreaded
environment, never use a database without initialize it first,
or connections will leak.

#### engine

Gives access to the engine

#### metadata

Proxy for `db.Model.metadata`

#### query

Proxy for `db.session.query`

#### add(\*args, \*\*kwargs)

Proxy for `db.session.add`

#### flush(\*args, \*\*kwargs)

Proxy for `db.session.flush`

#### commit()

Proxy for `db.session.commit`

#### rollback()

Proxy for `db.session.rollback`

#### create_all()

Creates all tables

#### drop_all()

Drops all tables

#### reflect(meta)

Reflects tables from the database

#### get_dataframe(query)

Converts a query into a Pandas DataFrame

```python
query = User.query
df = db.get_dataframe(query)

# or

df = db.get_dataframe(User.query.filter(User.name=='Dave'))
```

---

#### Method Chaining

For convenience, some method chaining are available

```python
    user = User(name="Mardix", location="Charlotte").save()

    User.get(12345).update(location="Atlanta")
```

---

#### Aggegated selects

```python
class Product(db.Model):
    name = db.Column(db.String(250))
    price = db.Column(db.Numeric)

price_label = db.func.sum(Product.price).label('price')
results = Product.query.filter(price_label)
```

---

## With Web Application

In a web application you need to call `db.session.remove()` after each response, and `db.session.rollback()` if an error occurs. However, if you are using Flask or other framework that uses the `after_request` and `on_exception` decorators, these bindings it is done automatically.

For example using Flask, you can do:

```python
app = Flask(__name__)

db = Database('sqlite://', app=app)
```

or

```python
db = Database()

app = Flask(__name__)

db.init_app(app)
```

### More examples

#### Many databases, one web app

```python
app = Flask(__name__)
db1 = Database(URI1, app)
db2 = Database(URI2, app)
```

#### Many web apps, one database

```python
db = Database(URI1)

app1 = Flask(__name__)
app2 = Flask(__name__)
db.init_app(app1)
db.init_app(app2)
```

---

## Pagination

All the results can be easily paginated

```python
users = User.query.paginate(page=2, per_page=20)
print(list(users))  # [User(21), User(22), User(23), ... , User(40)]
```

The paginator object it's an iterable that returns only the results for that page, so you use it in your templates in the same way than the original result:

```jinja
{% for item in paginated_items %}
    <li>{{ item.name }}</li>
{% endfor %}
```

Rendering the pages

Below your results is common that you want it to render the list of pages.

The `paginator.pages` property is an iterator that returns the page numbers, but sometimes not all of them: if there are more than 11 pages, the result will be one of these, depending of what is the current page:

Skipped page numbers are represented as `None`.

How many items are displayed can be controlled calling `paginator.iter_pages` instead.

This is one way how you could render such a pagination in your templates:

```jinja
{% macro pagination(paginator, endpoint=None, class_='pagination') %}
    {% if not endpoint %}
        {% set endpoint = request.endpoint %}
    {% endif %}
    {% if "page" in kwargs %}
        {% do kwargs.pop("page") %}
    {% endif %}
    <nav>
        <ul class="{{ class_ }}">
            {%- if paginator.has_prev %}
            <li><a href="{{ url_for(endpoint, page=paginator.prev_page_number, **kwargs) }}"
                rel="me prev"><span aria-hidden="true">&laquo;</span></a></li>
            {% else %}
            <li class="disabled"><span><span aria-hidden="true">&laquo;</span></span></li>
            {%- endif %}

            {%- for page in paginator.pages %}
            {% if page %}
                {% if page != paginator.page %}
                <li><a href="{{ url_for(endpoint, page=page, **kwargs) }}"
                    rel="me">{{ page }}</a></li>
                {% else %}
                <li class="active"><span>{{ page }}</span></li>
                {% endif %}
            {% else %}
                <li><span class=ellipsis>…</span></li>
            {% endif %}
            {%- endfor %}

            {%- if paginator.has_next %}
            <li><a href="{{ url_for(endpoint, page=paginator.next_page_number, **kwargs) }}"
                rel="me next">»</a></li>
            {% else %}
            <li class="disabled"><span aria-hidden="true">&raquo;</span></li>
            {%- endif %}
        </ul>
    </nav>
{% endmacro %}
```
