# SqlAlchemyTools

SqlAlchemyTools is a tool that provides similar functionality to Flask_SqlAlchemy without being dependant on Flask.

# Installation

Install SqlAlchemyTools with pip:

```
pip install sqlalchemy-tools
```

# Features

- Database:
  - Just by instantiating with Database(), SqlAlchemyTools automatically creates the session, model and everything necessary for SQLAlchemy.
  - Works with & without a Flask app with minimal code change
  - Thread safe by using [`scoped_session`](https://docs.sqlalchemy.org/en/13/orm/contextual.html)
  - Integration with Pandas to allow quick dataframe insertion and retriving queries as dataframes
  - It provides easy methods such as query(), create(), update(), delete(), to select, create, update, delete entries respectively.
  - Autogenerate the `__tablename__` as the snake case equivalent on the model name if not explictly defined (not pluralised)
  - It uses Arrow for DateTime
  - DateTime is saved in UTC and uses the ArrowType from the SQLAlchemy-Utils
  - Added some data types: JSONType, EmailType, and the whole SQLAlchemy-Utils Type
  - db.now -> gives you the Arrow UTC type
  - Paginated results
  - Pretty object representation
  - It is still SQLAlchemy. You can access all the SQLAlchemy awesomeness
- Migration:
  - Inbuilt migration support similar to Flask-migrate
  - Create a `manage.py` file to easily migrate your database
- ModelFrom:
  - Quickly add all the fields of a model to a WTF form
  - Supports `include`, `exclude`, `only`

# Quick Overview:

## Database

### Create the model

```python
from sqlalchemy_tools import Database

db = Database('sqlite://')

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = db.Column(db.String(25))
    location = db.Column(db.String(50), default="USA")
    last_access = db.Column(db.Datetime)
```

### Retrieve all records

```python
User.query.all()
```

### Create new record

```python
user = User.create(name="Mardix", location="Moon")

# or

user = User(name="Mardix", location="Moon").save()
```

### Get a record by primary key (id)

```python
user = User.get(1234)
```

### Update record from primary key

```python
user = User.get(1234)
if user:
    user.update(location="Neptune")
```

### Update record from query iteration

```python
for user in User.query:
    user.update(last_access=db.utcnow())
```

### Delete a record

```python
user = User.get(1234)
if user:
    user.delete()
```

### Query with filter

```python
all = User.query.filter(User.location == "USA")

for user in users:
    ...
```

## Migration

SqlAlchemyTools handles SQLAlchemy database migrations using Alembic. The database operations are made available through a command-line interface.

### Why use SqlAlchemyTools migration vs. Alembic directly

SqlAlchemyTools configures Alembic in the proper way to work with your database whether it is with or without Flask. In terms of the actual database migrations, everything is handled by Alembic so you get exactly the same functionality.

### Create `manage.py`

To support database migrations, you need to create a `manage.py` file.
> The file can be called anything

```python
from sqlalchemy_tools.migration import Migrate, migrate_manager
from sqlalchemy_tools import Database


# create/import your database
db = Database('sqlite:///tmp.db')

# create a `migrate` object that is linked to your database
migrate = Migrate(db)
migrate_manager.set_migrate(migrate)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128))


if __name__ == '__main__':
    migrate_manager.main()
```

### Initialise migrations folder

The `migrations` folder need to be initialise which will contain your database versions:

```bash
python manage.py init
```

### Create a new migration

Whenever there is a change to the models that you want reflected in the database:

```bash
python manage.py migrate -m "Intial migration"
```

### Upgrade database

To upgrade the database to the latest migration:

```bash
python manage.py upgrade
```

### Downgrade database

To downgrade the database by 1 migration:

```bash
python manage.py downgrade
```

### Help

To see all the commands that are available run:

```bash
python manage.py --help
```

## ModelForm

Make a Flask compatible version of the [**WTForms-Alchemy**](https://wtforms-alchemy.readthedocs.io/en/latest/index.html) ModelForm

```python
from sqlalchemy_tools import create_model_form
from sqlalchemy_tools import Database

# create/import your database
db = Database('sqlite:///tmp.db')
ModelForm = create_model_form(db)

class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['last_access']
```

# How to use

## Database

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



**BaseQuery**

The default model query is `from sqlalchemy_tools import BaseQuery`. It can be changed by using a different `query_cls` on initialising the database

```python
db = Database('sqlite://', query_cls=MyBaseQuery)
```

---

### db.Model Methods Description

#### query(\*args, \*\*kwargs)

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
