import datetime

from peewee import Model, ForeignKeyField, CharField, SqliteDatabase

db = SqliteDatabase('amazon.db')

class User(Model):
    telegramId = CharField(unique=True)
    class Meta:
        database = db # this model uses the "amazon.db" database


class Tracking(Model):
    user = ForeignKeyField(User, backref='user_id')
    asin = CharField()
    status = CharField()
    class Meta:
        database = db # this model uses the "amazon.db" database


# Create tables
db.connect()
db.create_tables([User, Tracking])