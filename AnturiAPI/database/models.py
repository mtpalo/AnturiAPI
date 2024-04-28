from sqlmodel import SQLModel, Field, Relationship, text
from sqlalchemy import UniqueConstraint, Index
from datetime import datetime
from .types import MittausTyyppi, TilaTyyppi
from pydantic import field_validator

import re

# lohkon ja anturin nimen validointi
def validoi(v: str):
    if len(v) < 5:
        raise ValueError("Nimen pituus on oltava vähintään 5 merkkiä!")
    if len(v) > 25:
        raise ValueError("Nimi on liian pitkä! Nimen maksimipituus on 25 merkkiä.")

    if not re.match('^[a-zA-Z0-9-_ ]+$', v):
        raise ValueError("Nimessä on oltava vain merkkejä 'a-zA-Z0-9-_ ' (välilyönti kelvollinen)")
    return v 

class AnturiBase(SQLModel):
    nimi: str

class AnturiLohkoIn(SQLModel):
    lohko: str

    _validoi_lohko = field_validator('lohko')(validoi)

class AnturiCreate(AnturiBase, AnturiLohkoIn):
    pass

    _validoi_nimi = field_validator('nimi')(validoi)
    _validoi_lohko = field_validator('lohko')(validoi)

# TAULU
class AnturiDB(AnturiCreate, table=True):
    __tablename__ = 'anturi'
    __table_args__ = (UniqueConstraint("nimi"), Index('ix_anturi_nimi', "nimi"),) # antureiden nimet on oltava uniikkeja

    # SARAKKEET
    id: int | None = Field(default=None, primary_key=True)
    tila: TilaTyyppi | None = Field(default=TilaTyyppi.NORMAALI)

    # SUHTEET
    # käännetään (order_by) anturin mittaukset ajan suhteen laskevaan järjestykseen (desc) anturin mittaus- ja tila-taulukot sa_relationship_kwargs
    # kääntämällä saadaan esimerkiksi 10 viimeisintä mittaustulosta listan alusta lukien
    mittaukset: list['AnturiMittausDB'] = Relationship(back_populates="anturi", sa_relationship_kwargs={"order_by": "desc(AnturiMittausDB.aikaleima)"})
    tilat: list['TilaDB'] = Relationship(back_populates="anturi", sa_relationship_kwargs={"order_by": "desc(TilaDB.aikaleima)"})
    # käännetään (order_by) anturin mittaukset ajan suhteen laskevaan järjestykseen (desc) ja asetetaan listan 1. tila nykyiseksi tilaksi (uselist: False)
    viimeisin_mittaus: 'AnturiMittausDB' = Relationship(back_populates="anturin_mittaus", sa_relationship_kwargs={"uselist": "False", "viewonly": "True", "order_by": "desc(AnturiMittausDB.aikaleima)"})

class AnturiBaseOut(SQLModel):
    id: int
    lohko: str

class AnturiTiedotOut(AnturiBaseOut):
    tila: TilaTyyppi | None = None
    mittaukset: list['AnturiMittausOut']

class AnturiTilaIn(SQLModel):
    tila: TilaTyyppi | None = None

class AnturiTilaOut(AnturiBaseOut):
    tila: TilaTyyppi = TilaTyyppi.NORMAALI

class AnturiMittausBase(SQLModel):
    mittaustulos: float | None

class AnturiMittausIn(AnturiMittausBase):
    tyyppi: MittausTyyppi | None = MittausTyyppi.TEMP

class AnturiMittausOut(AnturiMittausBase):
    aikaleima: datetime

class AnturiMittaus(AnturiMittausBase):
    mittaus_id: int
    anturi_id: int

# TAULU
class AnturiMittausDB(AnturiMittaus, table=True):
    __tablename__ = 'anturi_mittaus'

    # SARAKKEET
    id: int | None = Field(default=None, primary_key=True)
    mittaus_id: int = Field(default=None, foreign_key="mittaus.id")
    anturi_id: int = Field(default=None, foreign_key="anturi.id")
    # oletusarvona paikallinen aika (server_default)
    aikaleima: datetime | None = Field(default=None, index=True, sa_column_kwargs={"server_default": text("(DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))"),})

    # SUHTEET
    anturi: AnturiDB | None = Relationship(back_populates="mittaukset")
    anturin_mittaus: AnturiDB | None = Relationship(back_populates="viimeisin_mittaus", sa_relationship_kwargs={"viewonly": "True"})

class LohkoAnturiOut(AnturiMittausOut):
    id: int
    tila: TilaTyyppi = TilaTyyppi.NORMAALI

class MittausBase(SQLModel):
    tyyppi: MittausTyyppi | None = None

## TAULU
class MittausDB(MittausBase, table=True):
    __tablename__ = 'mittaus'
    __table_args__ = (UniqueConstraint("tyyppi"),) # mittaustyyppien on oltava uniikkeja ('LÄMPÖTILA')

    id: int | None = Field(default=None, primary_key=True)

class TilaBase(SQLModel):
    tila: TilaTyyppi = TilaTyyppi.NORMAALI
    # oletusarvona paikallinen aika (server_default)
    aikaleima: datetime | None = Field(default=None, index=True, sa_column_kwargs={"server_default": text("(DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME'))"),})

class TilaOut(TilaBase):
    pass

# TAULU
class TilaDB(TilaBase, table=True):
    __tablename__ = 'tila'

    # SARAKKEET
    id: int | None = Field(default=None, primary_key=True)
    anturi_id: int = Field(default=None, foreign_key="anturi.id")
    
    # SUHTEET
    anturi: AnturiDB | None = Relationship(back_populates="tilat")

class AnturiCreatedOut(TilaOut):
    anturi_id: int

class TilaErrorTimeOut(SQLModel):
    aikaleima: datetime