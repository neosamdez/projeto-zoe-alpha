import uuid
from fastapi import Header, HTTPException, status
from app.database import get_db

def get_tenant_id(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID", description="UUID do Tenant para Arquitetura Multi-Tenant")
) -> uuid.UUID:
    """Extração rigorosa e tipada do Tenant ID do Header."""
    try:
        tenant_uuid = uuid.UUID(x_tenant_id)
        return tenant_uuid
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header X-Tenant-ID inválido ou nulo. Esperado formato UUID válido."
        )
