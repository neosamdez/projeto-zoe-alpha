from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Engine Pool Stark: Conexão firme e resiliente ping-pong
engine = create_engine(settings.DB_URL, pool_pre_ping=True)

# Base da Sessão de Transações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Gerador Injetável (Dependency Injection do FastAPI).
    Tipado e com fechamento seguro de conexões.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
