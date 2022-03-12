from peewee import Model
from playhouse.sqlite_ext import SqliteExtDatabase


class BaseModel(Model):
    class Meta:
        database = SqliteExtDatabase("database.db")
