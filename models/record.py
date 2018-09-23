from peewee import *

from models import BaseModel


class Record(BaseModel):
    id = PrimaryKeyField()
    runner_id = IntegerField()
    game_id = IntegerField()
    time = IntegerField()
    date = DateTimeField()
    verified = BooleanField(default=False)

