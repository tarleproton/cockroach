from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image, ExifTags
import os
from models import Img


#преобразование координат
def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return float(decimal_degrees)


def get_lat_lon(file_name: str,
                img_name: str):
    # получение данных координат
    img_lat_lon = Image.open(file_name)
    try:
        exif = {ExifTags.TAGS[k]: v for k, v in img_lat_lon._getexif().items() if k in ExifTags.TAGS}
        lat_lon = str([decimal_coords(exif['GPSInfo'][2],
                                 exif['GPSInfo'][1]),
                  decimal_coords(exif['GPSInfo'][4],
                                 exif['GPSInfo'][3])])
        return lat_lon

    except:
        img_lat_lon.close()
        return None
        #os.remove(file_name)
        #raise HTTPException(status_code=500, detail=f'Изображении {file_name} не содержит координат')


#переименование файла в id
def rename_img(img,
               file_name: str,
               user: str,
               project_name: str,
               img_id
               ):
    img_type = img.content_type
    img_type = img_type.replace('image/', '')
    os.rename(file_name, f'img/{user}/{project_name}/{img_id}.{img_type}')


#сохранение данных в БД
async def save_img(project_id: int,
             lat_lon,
             img):

    img_type = img.content_type
    img_type = img_type.replace('image/', '')

    info = Img(project=project_id, coords=lat_lon, type_img=img_type)
    await Img.objects.create(**info.dict())

