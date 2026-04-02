"""
[DEPENDÊNCIAS INJETÁVEIS — AMENTI DEPENDENCY INJECTION]
Funções reutilizáveis que garantem autenticação, autorização e isolamento multi-tenant
em todas as rotas protegidas do sistema.
"""
import uuid
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_access_token
from app.models import User

# Esquema Bearer: aponta para o endpoint de login no Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_tenant_id(
    x_tenant_id: str = Header(..., alias="X-Tenant-ID", description="UUID do Tenant (multi-tenancy)")
) -> uuid.UUID:
    """Extração rigorosa e tipada do Tenant ID do Header."""
    try:
        return uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header X-Tenant-ID inválido. Esperado UUID v4 válido."
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    [DEPENDENCY: PROTEÇÃO JWT]
    Decodifica o Bearer Token, valida as claims e retorna o User autenticado.
    - Verifica assinatura e expiração do JWT
    - Garante que o usuário existe e está ativo no banco
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado. Autentique-se novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    email: str | None = payload.get("sub")
    user_id: str | None = payload.get("user_id")

    if not email:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Acesso ao Trono negado."
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency que exige role ADMIN. Protege rotas administrativas."""
    from app.models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a Administradores do Sistema."
        )
    return current_user
