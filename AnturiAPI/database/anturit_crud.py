from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import date, datetime


from .types import TilaTyyppi
from .models import (AnturiDB,
                     LohkoAnturiOut,
                     TilaDB,
                     AnturiTilaOut,
                     AnturiMittausDB,
                     AnturiMittausIn,
                     AnturiTiedotOut,
                     MittausDB,
                     AnturiMittaus)


def get_anturit(session: Session, tila: TilaTyyppi | None):
    """
    CRUD - READ
        listataan kaikki anturit
    
    Parametrit:
        tila (TilaTyyppi): listaus anturin tilan mukaan, jos annettu

        TilaTyyppi voi olla vain 'NORMAALI' tai 'VIRHE'
    """

    anturit = session.exec(select(AnturiDB)).all()
    if tila is not None:
        # listaus anturit tilan mukaan, tila.value -> Enum TilaTyyppi-arvo (NORMAALI|VIRHE)
        anturit = [anturi for anturi in anturit if anturi.tila == tila.value]
    result = []
    for anturi in anturit:
        a = AnturiTilaOut(tila=anturi.tila, id=anturi.id, lohko=anturi.lohko)
        result.append(a)
    return result

def get_lohko_anturit(anturit: list[AnturiDB]):
    """
    CRUD - READ
        haetaan kaikki tietyn lohkon anturit
    
    Parameterit:
        lohko (str): lohkon nimi, jonka anturit palautetaan
    """

    result = []
    # käydään lohkon anturit läpi yksitellen
    for anturi in anturit:
        tulos = LohkoAnturiOut(id=anturi.id,
                               tila=anturi.tila,                                                                                # viimeisin tila
                               mittaustulos=anturi.viimeisin_mittaus.mittaustulos if anturi.viimeisin_mittaus else None,        # viimeisin mittaustulos, jos on
                               aikaleima=anturi.viimeisin_mittaus.aikaleima if anturi.viimeisin_mittaus else None)              # viimeisin mittauksen aikaleima, jos on
        result.append(tulos)
    return result

def get_anturi(anturidb: AnturiDB,
               skip: int = 0,
               limit: int = 10,
               alkuaika: date | None = None,
               loppuaika: date | None = None):
    """
    CRUD - READ
        yksitäisen anturin tiedot

    Parametrit:
        anturidb (AnturiDB): anturi-taulun malli
        skip (int): mistä lähtien rajataan tuloksia
        limit (int): mihin asti rajataan tuloksia
        alkuaika (date): ei oletusarvoa
        loppuaika (date): oletuksena kuluva päivä
    """

    # rajataanko ajan suhteen (loppuaika on oletuksena annettu)
    if alkuaika is not None and loppuaika is not None:
        alku = datetime(alkuaika.year, alkuaika.month, alkuaika.day, 0, 0, 0)
        loppu = datetime(loppuaika.year, loppuaika.month, loppuaika.day, 23, 59, 59)
        mittaukset = [m for m in anturidb.mittaukset if m.aikaleima >= alku and m.aikaleima <= loppu]
    else:
        # ei rajata ajan suhteen, anturin mittaukset laskevassa järjestyksessä (anturidb.mittaukset)
        mittaukset = anturidb.mittaukset
    # montako tulosta näytetään
    anturi_mittaukset = mittaukset[skip : skip + limit]
    result = AnturiTiedotOut(id=anturidb.id,
                             lohko=anturidb.lohko,
                             tila=anturidb.tila,
                             mittaukset=anturi_mittaukset)
    return result


def create_mittaus(session: Session, anturidb: AnturiDB, mittaus_in: AnturiMittausIn):
    """
    CRUD - CREATE
        uusi anturin tekemä mittaus talteen

    Parametit:
        anturidb (AnturiDB): anturi-taulun malli
        mittaus_in (AnturiMittausIn):
                            mittaustulos (float): mittauksen tulos
                            aikaleima (datetime): oletusarvona on nykyinen aika (tietokanta)
                            tyyppi (MittausTyyppi): tyyppi voi olla tässä vaiheessa vain 'LÄMPÖTILA'
    """
    
    # tarkistetaan, että mittaustyyppi löytyy mittaus-taulusta
    statement = select(MittausDB).where(MittausDB.tyyppi == mittaus_in.tyyppi)
    mittausdb = session.exec(statement).first()
    if mittausdb is None:
        raise HTTPException(status_code=400, detail="Mittaustyyppi ei ole oikein! Admin voi lisätä mittaustyypin.")

    mittaus_in = AnturiMittaus(mittaustulos=round(mittaus_in.mittaustulos, 1), # pyöristetään tulos yhden desimaalin tarkkuuteen
                               mittaus_id=mittausdb.id,
                               anturi_id=anturidb.id)
    
    mittausdb = AnturiMittausDB.model_validate(mittaus_in, strict=True)
    session.add(mittausdb)
    session.commit()
    session.refresh(mittausdb)
    return mittausdb


def get_tila(anturi: AnturiDB):
    """
    CRUD - READ
        yksittäisen anturin kaikki tilamuutokset ajankohtineen
    
    Parametrit:
        anturi (AnturiDB): anturi-taulun malli
    """
    
    return anturi.tilat


def get_virhetilat(session: Session):
    """
    CRUD - READ
        virhetilanteiden esiintymisajankohdat
    """
    # uusin virhe ensin (order_by -> desc -> laskeva järjestys tila-taulun aikaleiman mukaan)
    statement = select(TilaDB).where(TilaDB.tila == TilaTyyppi.VIRHE).order_by(TilaDB.aikaleima.desc())
    virhetilat = session.exec(statement).all()
    return virhetilat

    