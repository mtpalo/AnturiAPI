from fastapi import HTTPException
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from .models import (AnturiLohkoIn,
                     AnturiCreate,
                     AnturiDB,
                     TilaDB,
                     AnturiMittausDB,
                     MittausDB,
                     MittausBase,
                     AnturiTilaIn)


def create_anturi(session: Session, anturi_in: AnturiCreate):
    """
    CRUD - CREATE
        lisää uusi anturi järjestelmään

    Parameterit:
        anturi_in (AnturiCreate):
                            nimi (str): lisättävän anturin nimi 
                            lohko (str): lisättävän anturin lohko
    """
    
    anturidb = AnturiDB.model_validate(anturi_in, strict=True)
    session.add(anturidb)
    try:
        session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Saman niminen anturi on jo tietokannassa!")
    session.refresh(anturidb)
    tiladb = TilaDB(anturi_id=anturidb.id)
    session.add(tiladb)
    session.commit()
    session.refresh(tiladb)
    return tiladb


def update_tila(anturi_tila_in: AnturiTilaIn, anturidb: AnturiDB, session: Session):
    """
    CRUD - UPDATE
        Anturin tilan päivitys -> lisätään uusi rivi tila-tauluun

    Parametrit:
        anturin_tila_in (AnturiTilaIn):
                            tila (TilaTyyppi): voi olla vain 'NORMAALI' tai 'VIRHE'
        
        anturidb (AnturiDB):
                    id (int): Anturin id anturi-taulussa
                    ...
    """

    tiladb = TilaDB(tila=anturi_tila_in.tila,
                    anturi_id=anturidb.id)
    anturidb.tila = anturi_tila_in.tila
    session.add(tiladb)
    session.commit()
    session.refresh(tiladb)
    return tiladb


def put_lohko(session: Session, anturidb: AnturiDB, anturi_in: AnturiLohkoIn):
    """
    CRUD - UPDATE
        päivitetään lohko, johon anturi kuuluu

    Parametrit:
        anturi_in (AnturiLohkoIn):
                        lohko (str): lohkon nimi, johon anturi päivitetään kuulumaan

        anturidb (AnturiDB): Anturi-taulun rivi, jonka lohko-sarakkeen arvo päivitetään
    """

    anturidb.lohko = anturi_in.lohko
    session.commit()
    session.refresh(anturidb)
    return anturidb


def delete_mittaus(session, mittausdb: AnturiMittausDB):
    """
    CRUD - DELETE
        yksittäisen mittauksen poistaminen

    Parametrit:
        mittausdb (AnturiDB): mittauksen rivi mittaus-taulussa, jota vastaava mittaus poistetaan
        
    """

    session.delete(mittausdb)
    session.commit()
    return {"Ok": True}


def create_mittaustyyppi(session: Session, mittaustyyppi_in: MittausBase):
    """
    CRUD - CREATE

    Parametrit:
        mittaustyyppi_in (MittausBase):
                                tyyppi (MittausTyyppi): oletuksena 'LÄMPÖTILA'
    """

    mittausdb = MittausDB(tyyppi=mittaustyyppi_in.TEMP)
    session.add(mittausdb)
    try:
        session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Mittaustyyppi on jo tietokannassa!")
    session.refresh(mittausdb)
    return mittausdb