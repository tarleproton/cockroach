from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import ValidationError
import shutil
import os
from services import get_lat_lon, rename_img, working_with_image
import aiofiles
from fastapi.responses import FileResponse

from schemas import EditImg, GetListProj, SizeImg, GetListCoords
from models import User, Project, Img
import uuid

photo_router = APIRouter()

#запись пользователей
@photo_router.post("/user_recording", response_model=User)
async def upload_user(user: str = Form(...)):

    user_list = await User.objects.filter(user_id=user).all()

    if not user_list:
        return await User.objects.create(user_id=user)

    else:
        raise HTTPException(status_code=500, detail='Пользователь уже существует')


#Запись данных о проекте в БД
@photo_router.post("/project_recording", response_model=Project)
async def upload_data(
                      user: str = Form(...),
                      project_name: str = Form(...),
                      description: str = Form(default=None)
                      ):

    user_list = await User.objects.filter(user_id=user).all()

    if user_list:

        os.makedirs(f"img/{user}/{project_name}")
        file_name = f'img/{user}/{project_name}'

        info = Project(user=user, project_name=project_name, description=description, path=file_name)

        return await Project.objects.create(**info.dict())

    else:
        raise HTTPException(status_code=500, detail='Пользователь не существует')


# Запись изображения
@photo_router.post("/img_recording")
async def upload_img(project_id: int = Form(...),
                      img: UploadFile = File(...)
                      ):
    img_type = img.content_type

    if 'image' in img_type:

        img_type = img_type.replace('image/', '')
        project_data_ = await Project.objects.get(id_project=project_id)

        # асинхронный вариант записи на диск
        async with aiofiles.open(f'{project_data_.path}/{img.filename}', "wb") as buffer:
            data = await img.read()
            await buffer.write(data)

        #запись размера файла
        size_img = os.path.getsize(f'{project_data_.path}/{img.filename}')/1000

        #получение координат
        #и сохранение превью

        lat_lon = await get_lat_lon(project_data_.path, img, project_id)

        if lat_lon == 'Изображении с такими координатами уже существует':
            raise HTTPException(status_code=500, detail='Изображении с такими координатами уже существует')

        elif lat_lon != None:

            img_id = await working_with_image(project_id, lat_lon, img_type, size_img)

            # получение id изображения для переименования файла
            img_id = await Img.objects.get(coords=lat_lon, project=project_id)
            img_id = img_id.id

            # переименование файла в id изображения(img_id)
            rename_img(img_type, project_data_.path, img_id, img.filename)

            # переименование файла превью
            rename_img(img_type, project_data_.path, str(img_id) + '_preview', img.filename + '_preview')

            #переименование файла превью
            # file_preview_name = file_name.replace(img.filename, img.filename + '_preview')
            # rename_img(img, file_preview_name, user, project_name, str(img_id) + '_preview')

            return {f'Загружен файл: {img_id}'}


        else:
            #Если у изображения нет координат
            lat_lon = str(uuid.uuid1())

            img_id = await working_with_image(project_id, lat_lon, img_type, size_img)

            # переименование файла в id изображения(img_id)
            rename_img(img_type, project_data_.path, img_id, img.filename)
            await Img.objects.filter(id=img_id).update(coords='')

            # переименование файла превью
            rename_img(img_type, project_data_.path, str(img_id) + '_preview', img.filename + '_preview')

            raise HTTPException(status_code=500, detail=f'Изображении {img_id} не содержит координат')


    else:
        raise HTTPException(status_code=500, detail='Загрузите изображение')


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


# #возврат данных по проектам пользователя из БД втч данных по координатам и их id
# @photo_router.get("/projects/{user_pk}", response_model=User)
# async def get_projects(user_pk: str):
#
#     user_list = await User.objects.filter(user_id=user_pk).all()
#
#     if user_list:
#         return await User.objects.select_all('projects').get(pk=user_pk)
#     else:
#         raise HTTPException(status_code=500, detail='Такого пользователя нет')


#возврат данных по проектам пользователя(данные урезаны по схеме GetListProj)
@photo_router.get("/projects_data/{user_pk}", response_model=list[GetListProj])
async def get_projects(user_pk: str):

    user_list = await User.objects.filter(user_id=user_pk).all()

    if user_list:

        return await Project.objects.filter(user=user_pk).all()
    else:
        raise HTTPException(status_code=500, detail='Такого пользователя нет')


# возврат данных по проекту
@photo_router.get("/project_data/{project_pk}")
async def get_project(project_pk: int):

    project_list = await Project.objects.filter(id_project=project_pk).all()

    if project_list:

        return await Project.objects.select_related('imgs').get(id_project=project_pk)

    else:
        raise HTTPException(status_code=500, detail='Такого проекта нет')



#возврат координат проекта
@photo_router.get("/coords_list/{project_pk}")
async def get_list_coords(project_pk: int):

    project_list = await Project.objects.filter(id_project=project_pk).all()

    if project_list:

        coords = await Img.objects.filter(project=project_pk).values()
        coords_list = [eval(item['coords']) for item in coords]
        sorted_coords_list = sorted(coords_list, key = lambda c: [c[1], c[0]])
        return sorted_coords_list

    else:
        raise HTTPException(status_code=500, detail='Такого проекта нет')

# возврат размера проекта
@photo_router.get("/size_project/{project_pk}")
async def size_project(project_pk: int):
    project_list = await Project.objects.filter(id_project=project_pk).all()

    if project_list:

        return await Img.objects.filter(project=project_pk).sum('size_img')
    else:
        raise HTTPException(status_code=500, detail='Такого проекта нет')

# размер всех проектов пользователя
@photo_router.get("/sum_size_project/{user_pk}")
async def sum_size_project(user_pk: str):

    user_list = await User.objects.filter(user_id=user_pk).all()

    if user_list:

        res = await Project.objects.select_related('imgs').filter(user=user_pk).fields(['size_img'])\
            .fields(['imgs__size_img']).values()

        list_img_size = [item['imgs__size_img'] for item in res]

        return sum(list_img_size)

    else:
        raise HTTPException(status_code=500, detail='Такого пользователя нет')


#возврат файла
#для возврата превью напишите , что угодно в preview
@photo_router.get("/img_response/{img_id}")
async def get_img(img_id: int,
                  preview: str = None):
    try:

        img_data = await Img.objects.select_related(Img.project).get(id=img_id)
        type_img = img_data.type_img
        patch = img_data.project.path

        if not preview:

            full_path = f'{patch}/{img_id}.{type_img}'

        else:

            full_path = f'{patch}/{img_id}_preview.{type_img}'

        return FileResponse(full_path)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f'{ex}')



# @photo_router.get("/img_response/{img_id}")
# async def get_img(img_id: int ):
#
#     try:
#
#         img_data = await Img.objects.select_related(Img.project).get(id=img_id)
#         type_img = img_data.type_img
#         patch = img_data.project.path
#
#         full_path = f'{patch}/{img_id}.{type_img}'
#
#         return FileResponse(full_path)
#
#     except Exception as ex:
#
#         raise HTTPException(status_code=500, detail=f'{ex}')


#удаление прокта и всех данных из ос
@photo_router.delete("/project_delete/{project_pk}")
async def del_project(project_pk: int):

    project_list = await Project.objects.filter(id_project=project_pk).all()

    if project_list:
        path = project_list[0].path
        shutil.rmtree(path)

        await Img.objects.delete(project=project_pk)
        await Project.objects.delete(id_project=project_pk)
        return {f'Проект {project_pk} удален'}
    else:
        raise HTTPException(status_code=500, detail='Такого проекта нет')


#удаление изображения из проекта
@photo_router.delete("/img_delete/{img_id}")
async def del_img(img_id: int): #os.remove()

    img_data = await Img.objects.select_related(Img.project).get(id=img_id)

    if img_data:

        path = img_data.project.path
        img_type = img_data.type_img

        #удаление файла
        os.remove(f'{path}/{img_id}.{img_type}')
        os.remove(f'{path}/{img_id}_preview.{img_type}')
        #удаление из БД
        await Img.objects.delete(id=img_id)
        return {f'Изображение {img_id} удалено'}


    else:
        raise HTTPException(status_code=500, detail='Нет такого изображения')

#редактирование координат изображения
@photo_router.post("/edit_coord")
async def edit_coord(edit_coord: EditImg):

    return await Img.objects.filter(id=edit_coord.img_id).update(coords=edit_coord.coord)







