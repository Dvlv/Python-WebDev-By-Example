from peewee import *

from models import BaseModel


class Runner(BaseModel):
    id = PrimaryKeyField()
    name = TextField()
    join_date = DateTimeField()
    country = TextField()


