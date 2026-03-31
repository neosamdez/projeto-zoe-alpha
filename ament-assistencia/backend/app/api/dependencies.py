import uuid
from typing import Generator
from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Injeta a sessão do banco de dados na requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant_id(
    x_tenant_id: str = Header(
        ..., 
        alias="X-Tenant-ID", 
        description="Tenant ID para isolamento de dados multitenant"
    )
) -> uuid.UUID:
    """
    Extrai o X-Tenant-ID do header da requisição e valida se é um UUID válido.
    Necessário em todas as rotas protegidas pelo isolamento do tenant.
    """
    try:
        tenant_uuid = uuid.UUID(x_tenant_id)
        return tenant_uuid
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header X-Tenant-ID ausente ou inválido. O fornecimento de um UUID válido é obrigatório."
        )
