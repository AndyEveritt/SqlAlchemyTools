from sqlalchemy_tools.migration import Manager, MigrateCommands, Migrate, MigrateManager
from sqlalchemy_tools import Database


db = Database('sqlite:///tmp.db')
migrate = Migrate(db)

MigrateCommands(migrate)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


if __name__ == '__main__':
    MigrateManager.main()
