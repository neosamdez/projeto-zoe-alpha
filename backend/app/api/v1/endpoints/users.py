import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user, require_admin
from app.schemas import UserResponse, UserUpdateByAdmin
from app.services.auth_service import AuthService
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Registro da Guilda: Lista todos os Operadores do Tenant. Acesso ADMIN."""
    service = AuthService(db, current_user.tenant_id)
    users = service.list_users()
    return [UserResponse.model_validate(u) for u in users]


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdateByAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Refino de Operador: Atualiza role/is_active/nome. Acesso ADMIN."""
    service = AuthService(db, current_user.tenant_id)
    user = service.update_user(user_id, user_in)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Expurgo de Operador: Soft delete. Acesso ADMIN. Não pode deletar a si mesmo."""
    if str(user_id) == str(current_user.id):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operador não pode remover a si mesmo."
        )
    service = AuthService(db, current_user.tenant_id)
    service.delete_user(user_id)
    return None
