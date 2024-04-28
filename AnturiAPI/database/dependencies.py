from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from ..database.database import get_session
from .models import AnturiDB, AnturiMittausDB, AnturiTilaIn


def get_anturi_by_name(nimi: str, session: Session = Depends(get_session)):
    """
    Parametrit:
        nimi (str): anturin nimi (polkuparametrista)

    Palauttaa anturin nimeä vastaavan anturi-taulun rivin
    """

    statement = select(AnturiDB).where(AnturiDB.nimi == nimi)
    anturidb = session.exec(statement).first()
    if anturidb is None:
        raise HTTPException(status_code=404, detail="Anturia ei löytynyt tietokannasta!")
    return anturidb


def get_anturit_by_lohko(lohko: str, session: Session = Depends(get_session)):
    """
    Parametrit:
        lohko (str): lohkon nimi

    Palauttaa lohkon anturit
    """

    statement = select(AnturiDB).where(AnturiDB.lohko == lohko)
    anturit = session.exec(statement).all()
    if len(anturit) == 0:
        raise HTTPException(status_code=404, detail="Lohkoa ei tietokannassa!")
    return anturit


def valid_mittaus_id(id: int, session: Session = Depends(get_session)):
    """
    Parametrit:
        id (int): taulun id-arvo (polkuparametri)

    Palauttaa id-arvoa (polkuparametri) vastaavan rivin, joka poistetaan taulusta
    """

    mittausdb = session.get(AnturiMittausDB, id)
    if mittausdb is None:
        raise HTTPException(status_code=404, detail="Mittausta ei tietokannassa!")
    return mittausdb


def valid_tilamuutos(anturi_tila_in: AnturiTilaIn, anturidb: AnturiDB = Depends(get_anturi_by_name)):
    """
    Tarkistaa, että tilamuutos tehdään vain jos tila todella muuttuu: 'VIRHE' -> 'NORMAALI' tai 'NORMAALI' -> 'VIRHE'
    
    Parametrit:
        anturi_tila_in (AnturiTilaIn): TilaTyyppi -> arvo, johon muutos halutaan tehdä
        anturidb (AnturiDB): nimeä vastaava anturi-taulun rivi, jonka tila-sarakkeen arvo tarkastetaan

    Palauttaa tilan joka annettiin
    """

    # päivitetään anturin tila vain, jos anturin tila muuttuu
    if anturidb.tila == anturi_tila_in.tila:
        raise HTTPException(status_code=400, detail=f"Anturi on jo tilassa {anturi_tila_in.tila}!")
    return anturi_tila_in