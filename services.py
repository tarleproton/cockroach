from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image, ExifTags

################################
#преобразование координат
def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return float(decimal_degrees)
#################################


def get_lat_lon(file_name: str):
    # получение данных координат
    img_lat_lon = Image.open(file_name)
    exif = {ExifTags.TAGS[k]: v for k, v in img_lat_lon._getexif().items() if k in ExifTags.TAGS}
    lat_lon = str([decimal_coords(exif['GPSInfo'][2],
                             exif['GPSInfo'][1]),
              decimal_coords(exif['GPSInfo'][4],
                             exif['GPSInfo'][3])])
    return lat_lon





