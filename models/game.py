from peewee import *

from models import BaseModel


class Game(BaseModel):
    id = PrimaryKeyField()
    title = TextField()
    platform = TextField()
    release_year = TextField()

    def update_from_form(self, data):
        self.title = data["title"]
        self.platform = data["platform"]
        self.release_year = data["release_year"]

        self.save()
