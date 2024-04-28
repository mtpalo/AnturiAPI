
from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from datetime import date

from ..database.types import TilaTyyppi
from ..database import anturit_crud
from ..database.models import (AnturiDB,
                               TilaOut,
                               TilaErrorTimeOut,
                               AnturiTilaOut,
                               LohkoAnturiOut,
                               AnturiMittausIn,
                               AnturiMittausDB,
                               AnturiTiedotOut)
from ..database.database import get_session
from ..database.dependencies import get_anturi_by_name, get_anturit_by_lohko

router = APIRouter(prefix="/anturit")

# GET -> kaikki anturit
@router.get("/", response_model=list[AnturiTilaOut], tags=["read_anturit"])
def get_anturit(tila: TilaTyyppi | None = None, session: Session = Depends(get_session)):
    return anturit_crud.get_anturit(session, tila)

# GET -> kaikki tietyn lohkon anturit
@router.get("/{lohko}", response_model=list[LohkoAnturiOut], tags=["read_lohkon_anturit"])
def get_lohko_anturit(anturit: list[AnturiDB] = Depends(get_anturit_by_lohko)):
    return anturit_crud.get_lohko_anturit(anturit)

# GET -> yksittäisen anturin kaikki tiedot
@router.get("/{nimi}/tiedot", response_model=AnturiTiedotOut, tags=["read_anturin_tiedot"])
def get_anturi(anturi: AnturiDB = Depends(get_anturi_by_name),
               skip: int = 0,
               limit: int = 10,
               alkuaika: date = Query(None, description="Päivämäärä muodossa YYYY-MM-DD"),
               loppuaika: date = Query(date.today(), description="Päivämäärä muodossa YYYY-MM-DD")):    # loppuajan oletusarvona kuluva päivä
    return anturit_crud.get_anturi(anturi, skip, limit, alkuaika, loppuaika)

# POST -> anturin mittaus
@router.post("/{nimi}/mittaus", response_model=AnturiMittausDB, status_code=status.HTTP_201_CREATED, tags=["create_mittaus"])
def post_mittaus(mittaus_in: AnturiMittausIn,
                 anturi: AnturiDB = Depends(get_anturi_by_name),
                 session: Session = Depends(get_session)):
    return anturit_crud.create_mittaus(session, anturi, mittaus_in)

# GET -> yksittäisen anturin kaikki tilamuutokset ajankohtineen
@router.get("/{nimi}/tila", response_model=list[TilaOut], tags=["read_anturin_tilamuutokset"])
def get_tila(anturi: AnturiDB = Depends(get_anturi_by_name)):
    return anturit_crud.get_tila(anturi)

# GET -> antureiden virhetilanteet
@router.get("/tila/virheet", response_model=list[TilaErrorTimeOut], tags=["read_virhetilanteet"])
def get_virhetilat(session: Session = Depends(get_session)):
    return anturit_crud.get_virhetilat(session)
