from peewee import *

from models import BaseModel


class Game(BaseModel):
    id = PrimaryKeyField()
    title = TextField()
    platform = TextField()
    release_year = TextField()
