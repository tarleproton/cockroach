from pydantic import BaseModel, validator
from typing import List
import datetime
import re

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

class EditImg(BaseModel):
    img_id: int
    coord: str

    @validator('coord')
    def coord_should_be(cls, c: str):
        #проверка корректности координат
        #если хоть одна из координат не соответствует \d{2}\.\d+ (пример 54.32256), вернем ошибку

        coords_list = re.findall(r"\d+\.\d+", c)
        if len(coords_list) == 2:
            for coord in coords_list:
                if not re.fullmatch(r"\d{2}\.\d+", coord):
                    raise ValueError('Формат координаты не верен')

            return f'{[float(coords_list[0]), float(coords_list[1])]}'

        raise ValueError('Формат координаты не верен')


