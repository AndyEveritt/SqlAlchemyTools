from sqlalchemy_tools.migration import Manager, Migrate, migrate_manager
from sqlalchemy_tools import Database


db = Database('sqlite:///tmp.db')
migrate = Migrate(db)

migrate_manager.set_migrate(migrate)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


if __name__ == '__main__':
    migrate_manager.main()
