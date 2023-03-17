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


async def img_info(path: str,
                img,
                project_id: int):
    # получение данных координат
    img_name = img.filename
    img_lat_lon = Image.open(f'{path}/{img_name}')

    try:
        exif = {ExifTags.TAGS[k]: v for k, v in img_lat_lon._getexif().items() if k in ExifTags.TAGS}
        lat_lon = str([decimal_coords(exif['GPSInfo'][2],
                                 exif['GPSInfo'][1]),
                  decimal_coords(exif['GPSInfo'][4],
                                 exif['GPSInfo'][3])])
        date_time = exif['DateTimeOriginal']


        img_in_bd = await Img.objects.filter(coords=lat_lon, project=project_id).all()

        if not img_in_bd:

            return [lat_lon, date_time]
        else:
            img_lat_lon.close()
            os.remove(f'{path}/{img_name}')
            return ['Изображении с такими координатами уже существует', None]

    except:

        return [None, None]

    finally:
        try:
            img_lat_lon.thumbnail((64, 64))
            img_lat_lon.save(f'{path}/{img.filename}_preview', "JPEG")
            img_lat_lon.close()
        except:
            pass



#переименование файла в id
def rename_img(img_type,
               path: str,
               img_id: int,
               img_name: str,
               ):

    os.rename(f'{path}/{img_name}', f'{path}/{img_id}.{img_type}')


#сохранение данных в БД
async def save_img_data(project_id: int,
             lat_lon: str,
             img_type: str,
             size_img:int,
             date_time:str):

    info = Img(project=project_id, coords=lat_lon, type_img=img_type, size_img=size_img, img_date=date_time)
    await Img.objects.create(**info.dict())


async def working_with_image(project_id, lat_lon, img_type, size_img, date_time):
    # сохранение данных в БД
    await save_img_data(project_id, lat_lon, img_type, size_img, date_time)

    # получение id изображения для переименования файла
    img_id = await Img.objects.get(project=project_id, coords=lat_lon)
    img_id = img_id.id
    return img_id

