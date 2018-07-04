import datetime

from peewee import (Model, DateTimeField, ForeignKeyField, BigIntegerField, CharField, IntegerField, TextField, OperationalError, BooleanField)


class User(Model):
    telegramId = CharField(unique=True)
    #known_at = DateTimeField(default=datetime.datetime.now)
    #name = CharField()
    #last_fetched = DateTimeField(default=datetime.datetime.now)

    #@property
    #def full_name(self):
    #    return "{} ({})".format(self.name, self.screen_name)

class Tracking(Model):
    ForeignKeyField(User, related_name="telegramId")
    asin = CharField()



# Create tables
for t in (User, Tracking):
    t.create_table(fail_silently=True)