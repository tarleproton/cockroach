import ormar
from db import metadata, database
import datetime
from typing import Optional

class User(ormar.Model):
    class Meta:
        tablename = "users"
        metadata = metadata
        database = database

    user_id: str = ormar.String(primary_key=True, max_length=150)


class Project(ormar.Model):
    class Meta:
        tablename = "projects"
        metadata = metadata
        database = database

    id_project: int = ormar.Integer(primary_key=True)
    user: Optional[User] = ormar.ForeignKey(User)
    project_name:str =ormar.String(max_length=100)
    description: str = ormar.String(max_length=500, nullable=True)
    path: str = ormar.String(max_length=1000, nullable=True)
    create_date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())
    #coords: str = ormar.JSON(nullable=True)


class Img(ormar.Model):
    class Meta:
        tablename = "imgs"
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    project: Optional[Project] = ormar.ForeignKey(Project)
    coords: str = ormar.String(max_length=100, nullable=True)
    type_img: str = ormar.String(max_length=50)
    size_img: int = ormar.Integer()
    img_date: str = ormar.String(max_length=100, nullable=True)


# class Photo(ormar.Model):
#     class Meta(MainMeta):
#         pass
#     user_id: int = ormar.Integer(primary_key=True)
#     user: Optional[Photo] = ormar.ForeignKey(Photo)
#     user_name: str =ormar.String(max_length=100)
#     project_name:str =ormar.String(max_length=50)
#     description: str = ormar.String(max_length=500)
#     path: str = ormar.String(max_length=1000)
#     create_date: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())
#     coords: str = ormar.JSON()

# class Coords(ormar.Model):
#     class Meta(MainMeta):
#         pass
#
#     user_id: Optional[Photo]= ormar.ForeignKey(Photo)
#     project_name: Optional[Photo]= ormar.ForeignKey(Photo)
#     coords: str = ormar.String(max_length=500)