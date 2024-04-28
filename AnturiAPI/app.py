from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from .routers import admin, anturit
from .tags import tags_metadata
from .database.database import create_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startataan")
    # luo tietokanta
    create_db()
    yield
    print("lopetellaan")

description = "API Anturien mittausdatalle"

app = FastAPI(
    title="Mittausdata sovellus" ,
    description=description,
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(admin.router)
app.include_router(anturit.router)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "AnturiAPI"}