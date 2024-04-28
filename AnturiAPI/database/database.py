from sqlmodel import Session, create_engine, SQLModel

# default tietokanta
DATABASE = f"sqlite:///anturit.db"
connect_args = {'check_same_thread': False}

# testitietokantaa varten tämä
def get_engine(db: str = DATABASE):
    return create_engine(db, echo=True, connect_args=connect_args)

engine = get_engine(DATABASE)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
