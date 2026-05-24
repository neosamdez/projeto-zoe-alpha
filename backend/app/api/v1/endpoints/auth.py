"""
[ENDPOINT: AUTH ROUTER — PORTÃO DE ACESSO]
Rotas de autenticação. Usa OAuth2PasswordRequestForm para compatibilidade
nativa com Swagger UI (botão "Authorize" funcional).
"""
import uuid
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.dependencies import get_tenant_id, get_current_user
from app.models import User
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.schemas import Token, UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    summary="Login do Operador",
    description="Recebe e-mail e senha. Valida credenciais e retorna um Bearer Token JWT."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    [POST /auth/login]
    - username = e-mail do Operador (padrão OAuth2PasswordRequestForm)
    - password = senha em texto plano
    Retorna: { access_token, token_type: 'bearer' }
    """
    service = AuthService(db=db)
    user = service.authenticate_user(email=form_data.username, password=form_data.password)

    token_data = {
        "sub": user.email,
        "tenant_id": str(user.tenant_id),
        "role": user.role.value,
        "user_id": str(user.id),
    }
    access_token = create_access_token(data=token_data)

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Perfil do Operador",
    description="Retorna os dados do usuário autenticado via Bearer Token."
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de novo Operador",
    description="Cria um novo usuário no Tenant. Requer Header X-Tenant-ID."
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    [POST /auth/register]
    Registra um novo Operador. Hasheia a senha e isola por tenant_id.
    """
    service = AuthService(db=db)
    user = service.register_user(user_in=user_in)
    return UserResponse.model_validate(user)
