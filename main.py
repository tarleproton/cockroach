from fastapi import FastAPI
from api import photo_router
from db import engine, metadata, database

#uvicorn main:app   #если нужно перезагрузка при изменениях то с опцией - reload

def get_application() -> FastAPI:
    application = FastAPI()
    return application

app = get_application()

#metadata.create_all(engine) #создание БД
app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


app.include_router(photo_router)



