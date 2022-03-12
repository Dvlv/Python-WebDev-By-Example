from models import BaseModel
from playhouse.sqlite_ext import *


class Product(BaseModel):
    id = AutoField()
    name = TextField()
    price = TextField()

    class Meta:
        table_name = "product"
