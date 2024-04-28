
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from ..database import admin_crud
from ..database.models import MittausBase, MittausDB
from ..database.database import get_session
from ..database.dependencies import get_anturi_by_name, valid_mittaus_id, valid_tilamuutos
from ..database.models import (AnturiDB,
                               AnturiBaseOut,
                               AnturiCreate,
                               AnturiLohkoIn,
                               AnturiMittausDB,
                               AnturiTilaIn,
                               AnturiCreatedOut)

router = APIRouter(prefix="/admin")

# POST -> uuden anturin lisääminen
@router.post("/anturit", response_model=AnturiCreatedOut, status_code=status.HTTP_201_CREATED, tags=["admin_create_anturi"])
def post_anturi(anturi_in: AnturiCreate, session: Session = Depends(get_session)):
    return admin_crud.create_anturi(session, anturi_in)

# POST - anturin tilan muutos/päivitys
@router.post("/anturit/{nimi}/tila", response_model=AnturiCreatedOut, tags=["admin_update_anturin_tila"])
def post_tila(anturi_tila_in: AnturiTilaIn = Depends(valid_tilamuutos),
              anturi: AnturiDB = Depends(get_anturi_by_name),
              session: Session = Depends(get_session)):
    return admin_crud.update_tila(anturi_tila_in, anturi, session)

# PUT -> anturin lohkon päivitys
@router.put("/anturit/{nimi}/lohko", response_model=AnturiBaseOut, status_code=status.HTTP_200_OK, tags=["admin_update_lohko"])
def put_lohko(anturi_in: AnturiLohkoIn,
              anturi: AnturiDB = Depends(get_anturi_by_name),
              session: Session = Depends(get_session)):
    return admin_crud.put_lohko(session, anturi, anturi_in)

# DELETE -> yksittäisen mittaustuloksen poistaminen
@router.delete("/anturit/mittaus/{id}", tags=["admin_delete_mittaus"])
def delete_mittaus(mittausdb: AnturiMittausDB = Depends(valid_mittaus_id),
                   session: Session = Depends(get_session)):
    return admin_crud.delete_mittaus(session, mittausdb)

# POST -> mittaustyypin lisääminen
@router.post("/mittaus", response_model=MittausDB, status_code=status.HTTP_201_CREATED, tags=["admin_create_mittaustyyppi"])
def post_mittaustyyppi(mittaustyyppi_in: MittausBase, session: Session = Depends(get_session)):
    return admin_crud.create_mittaustyyppi(session, mittaustyyppi_in.tyyppi)