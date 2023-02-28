from pydantic import BaseModel
from typing import List
import datetime

#модель загрузки данных в БД
class UploadDate(BaseModel):

    #identification: List[str] = None #аргумент может отсутствовать
    #coords: List[str]

    user_id:int
    project: str
    description: str = None
    layer: str
    path: str
    create_date: datetime.datetime = None
    user: int

#модель получения данных о проетах пользователя
#использовать если хочется сократить список полей данных на выход
#нужно пофиксить , данные не корректны
class GetProject(BaseModel):
    #photo: Coords
    user: UploadDate

class GetListCoords(BaseModel):
    coords: str
