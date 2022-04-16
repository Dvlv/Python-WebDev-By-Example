from models import BaseModel
from playhouse.sqlite_ext import *


class Order(BaseModel):
    id = AutoField()
    timestamp_created = DateTimeField()
    email = TextField()
    products = JSONField()
