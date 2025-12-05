from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./clasificador.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Importar modelos
from app.models.machine_template_model import MachineTemplate
from app.models.machine_model import Machine
from app.models.package_model import Package
from app.models.package_part_model import PackagePart
from app.models.distribucion_storage_model import DistribucionStorage
from app.models.estilo_manual_model import EstiloManual

# Crear tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()