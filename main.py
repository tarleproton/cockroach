from fastapi import FastAPI
from api import photo_router
from db import engine, metadata, database
from fastapi.middleware.cors import CORSMiddleware

# import logging
# level = logging.DEBUG
# FORMAT = '%(asctime)s %(processName)s\%(name)-8s %(levelname)s: %(message)s'
# logfile = 'C:\cockroach\my.log'
# logging.basicConfig(format = FORMAT, level=level, filename = logfile )
#
# logger = logging.getLogger(__name__)
# debug = logger.debug
# print = logger.info

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://view-360-two.vercel.app",
]

#uvicorn main:app   #если нужно перезагрузка при изменениях то с опцией - reload

def get_application() -> FastAPI:
    application = FastAPI()
    return application

app = get_application()

metadata.create_all(engine) #создание БД
app.state.database = database

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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



