from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import shutil
import os
from services import get_lat_lon
import aiofiles
from fastapi.responses import FileResponse


from schemas import UploadDate, GetProject, GetListCoords
from models import User, Project, Img

photo_router = APIRouter()



#запись пользователей
@photo_router.post("/user_recording", response_model=User)
async def upload_user(user: int = Form(...)):

    user_list = await User.objects.filter(user_id=user).all()

    if not user_list:
        return await User.objects.create(user_id=user)

    else:
        raise HTTPException(status_code=500, detail='Пользователь уже существует')


#Запись данных о проекте в БД
@photo_router.post("/data_recording")
async def upload_data(
                      user: int = Form(...),
                      project_name: str = Form(...),
                      description: str = Form(default=None)
                      ):

    os.makedirs(f"img/{user}/{project_name}")
    #file_name = f'img/{img.filename}'
    file_name = f'img/{user}/{project_name}'

    info = Project(user=user, project_name=project_name, description=description, path=file_name)

    #return {'headers': img.headers, 'size': img.size, 'coords':coords, 'info':info}
    return await Project.objects.create(**info.dict())
#test
@photo_router.post("/test")
async def test( project: int = Form(...),
                img: UploadFile = File(...)
                      ):
    project_name = await Project.objects.filter(id_project=project).all()

    return (project_name[0].dict().get('project_name'))


#Запись изображения
@photo_router.post("/img_recording")
async def upload_img(project_id: int = Form(...),
                      img: UploadFile = File(...)
                      ):

    project_data = await Project.objects.filter(id_project=project_id).all()
    user = project_data[0].dict().get('user').get('user_id')
    project_name = project_data[0].dict().get('project_name')


    file_name = f'img/{user}/{project_name}/{img.filename}'

    # with open(file_name, "wb") as buffer:
    #     shutil.copyfileobj(img.file, buffer)

    # асинхронный вариант записи на диск
    async with aiofiles.open(file_name, "wb") as buffer:
        data = await img.read()
        await buffer.write(data)

    lat_lon = get_lat_lon(file_name)

    #переименование файла в координаты
    os.rename(file_name, f'img/{user}/{project_name}/{lat_lon}.JPG')

    info = Img(project=project_id, coords=lat_lon)

    return await Img.objects.create(**info.dict())


#загрузка нескольких фоток
# @photo_router.post("/upload_photos")
# async def root(photos: List[UploadFile] = File(...)):
#
#     for photo in photos:
#         file_name = f'img/{photo.filename}'
#
#         with open(f"{file_name}", "wb") as f:
#             shutil.copyfileobj(photo.file, f)
#
#     return {"file_name": "Ok"}

# @photo_router.post("/info")
# async def info_set(info: User):
#     await info.save()
#     return info


#возврат данных по проекту из БД
@photo_router.get("/projects/{user_pk}", response_model=User)
async def get_projects(user_pk: int):

    return await User.objects.select_related('projects').get(pk=user_pk)

# возврат координат проекта
# @photo_router.get("/coords/{project_pk}", response_model=Project)
# async def get_coords(project_pk: int):
#
#     return await Project.objects.select_related('imgs').get(pk=project_pk)

# возврат координат проекта
@photo_router.get("/coords_list/{project_pk}", response_model=List[GetListCoords])
async def get_list_coords(project_pk: int):

    coord_list = await Img.objects.filter(project=project_pk).all()
    return coord_list

#возврат файла
@photo_router.get("/img_response/{file_name}")
async def get_img(file_name: str):
    return FileResponse(file_name)

#file_name = 'img\GSAU1287.JPG'

