from fastapi.testclient import TestClient
from AnturiAPI.app import app
from AnturiAPI.database import database
from AnturiAPI.database.models import *
from AnturiAPI.database.types import TilaTyyppi, MittausTyyppi

import pytest

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture(scope="session")
def test_db():

    # testitietokanta
    DATABASE = f"sqlite:///test.db"

    test_engine = database.get_engine(DATABASE)

    database.engine = test_engine

    # alustetaan mallin mukainen tietokanta
    SQLModel.metadata.create_all(test_engine)

    yield

    # lopuksi tyhjennetään tietokanta
    SQLModel.metadata.drop_all(test_engine)

anturi = {"nimi": "Anturi11", "lohko": "A13_13"}
anturi_invalid = {"nimi": "A123", "lohko": "A13_13"}        # nimi liian lyhyt (vähintään 5 merkkiä tulisi olla)
puuttuva_anturi = {"nimi": "Anturi10", "lohko": "A13_13"}
mittaustulos = 15.0
uusi_lohko = "Lohko B1_2"

def test_read_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "AnturiAPI"}


def test_read_anturit(client):
    res = client.get("/anturit/")
    assert res.status_code == 200
    assert res.json() == []

def test_read_lohkon_anturit_puuttuva(client):
    res = client.get(f"/anturit/{uusi_lohko}")
    assert res.status_code == 404
    data = res.json()
    assert data['detail'] == "Lohkoa ei tietokannassa!"

def test_create_anturi(client):
    res = client.post("/admin/anturit/", json=anturi)
    assert res.status_code == 201
    data = res.json()
    assert data['anturi_id'] == 1
    assert data['tila'] == TilaTyyppi.NORMAALI
    assert 'aikaleima' in data


def test_create_anturi_nimi_liian_lyhyt(client):
    res = client.post("/admin/anturit/", json=anturi_invalid)
    assert res.status_code == 422
    data = res.json()
    assert data['detail'][0]['type'] == 'value_error'
 

def test_update_lohko(client):
    res = client.put(f"/admin/anturit/{anturi['nimi']}/lohko", json={"lohko": uusi_lohko})
    assert res.status_code == 200
    assert res.json() == {
        "id": 1,
        "lohko": uusi_lohko
    }


def test_create_duplicate_anturi(client):
    res = client.post("/admin/anturit/", json=anturi)
    assert res.status_code == 400
    assert res.json() == {"detail": "Saman niminen anturi on jo tietokannassa!"}


def test_create_mittaustyyppi(client):
    res = client.post("/admin/mittaus", json={"tyyppi": MittausTyyppi.TEMP})
    assert res.status_code == 201
    assert res.json() == {"tyyppi": MittausTyyppi.TEMP, "id": 1}


def test_create_mittaus(client):
    res = client.post(f"/anturit/{anturi['nimi']}/mittaus", json={"mittaustulos": mittaustulos})
    assert res.status_code == 201
    data = res.json()
    assert data['mittaustulos'] == mittaustulos
    assert 'aikaleima' in data
    assert data['anturi_id'] == 1
    assert data['mittaus_id'] == 1


def test_read_anturi(client):
    res = client.get(f"/anturit/{anturi['nimi']}/tiedot")
    assert res.status_code == 200
    data = res.json()
    assert data['lohko'] == uusi_lohko
    assert len(data['mittaukset']) == 1
    assert data['id'] == 1
    assert 'aikaleima' in data['mittaukset'][0]
    assert data['mittaukset'][0]['mittaustulos'] == mittaustulos
    assert data['tila'] == TilaTyyppi.NORMAALI


def test_read_puuttuva_anturi(client):
    res = client.get(f"/anturit/{puuttuva_anturi}/tiedot",)
    assert res.status_code == 404
    assert res.json() == {"detail": "Anturia ei löytynyt tietokannasta!"}


def test_update_tila(client):
    res = client.post(f"/admin/anturit/{anturi['nimi']}/tila", json={"tila": TilaTyyppi.VIRHE})
    assert res.status_code == 200
    data = res.json()
    assert data['tila'] == TilaTyyppi.VIRHE
    assert data['anturi_id'] == 1
    assert 'aikaleima' in data


def test_read_lohkon_anturit(client):
    res = client.get(f"/anturit/{uusi_lohko}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    data = data[0]
    assert data['mittaustulos'] == mittaustulos
    assert 'aikaleima' in data
    assert data['id'] == 1
    assert data['tila'] == TilaTyyppi.VIRHE


def test_delete_mittaus(client):
    mittauksen_id = 1 
    res = client.delete(f"/admin/anturit/mittaus/{mittauksen_id}")
    assert res.status_code == 200
    assert res.json() == {"Ok": True}


def test_get_tilamuutokset(client):
    res = client.get(f"/anturit/{anturi['nimi']}/tila")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


def test_get_virhetilat(client):
    res = client.get("/anturit/tila/virheet")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert 'aikaleima' in data[0]