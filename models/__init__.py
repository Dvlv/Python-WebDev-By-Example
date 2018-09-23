from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = db

    def update_from_form(self, data):
        for k, v in data.items():
            setattr(self, k, v)

        self.save()
