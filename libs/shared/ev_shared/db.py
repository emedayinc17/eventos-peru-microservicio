from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Engine global, reusado por servicio
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency para inyectar Session por request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
