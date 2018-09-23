from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

database = SqliteExtDatabase("database.db")


class BaseModel(Model):
    class Meta:
        database = database

