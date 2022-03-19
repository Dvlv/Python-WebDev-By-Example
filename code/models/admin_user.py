from models import BaseModel
from playhouse.sqlite_ext import *


class AdminUser(BaseModel):
    id = AutoField()
    username = TextField()
    password = TextField()

    class Meta:
        table_name = "admin_user"
