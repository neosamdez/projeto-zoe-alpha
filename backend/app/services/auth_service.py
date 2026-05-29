"""
[SERVIÇO: AUTH SERVICE — CAMADA DE NEGÓCIO]
Lógica de autenticação e gestão de utilizadores.
Princípio Amenti: regras de negócio vivem no Service, nunca no Controller.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate, UserUpdateByAdmin
from app.core.security import get_password_hash, verify_password
from datetime import datetime, timezone


class AuthService:
    def __init__(self, db: Session, tenant_id: uuid.UUID = None):
        self.db = db
        self.tenant_id = tenant_id

    def register_user(self, user_in: UserCreate) -> User:
        """
        Registra um novo Operador.
        Trava de duplicidade: e-mail único por tenant (tenant_id + email).
        Role SEMPRE TECHNICIAN — atribuição de ADMIN só via UserUpdateByAdmin.
        Se não houver tenant_id vinculado (Módulo Público), forja uma nova Cidadela (Tenant).
        """
        from app.models import UserRole

        final_tenant_id = self.tenant_id or uuid.uuid4()

        existing = (
            self.db.query(User)
            .filter(User.email == user_in.email, User.tenant_id == final_tenant_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"E-mail '{user_in.email}' já possui registro neste tenant."
            )

        new_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=UserRole.TECHNICIAN,
            tenant_id=final_tenant_id,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, email: str, password: str) -> User:
        """
        Valida credenciais de forma global no ecosistema.
        Nunca revela se foi o e-mail ou a senha que falhou (segurança por design).
        """
        user = (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas. Acesso negado.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo. Contate o administrador.",
            )
        return user

    def list_users(self) -> list[User]:
        """Lista todos os Operadores ativos do Tenant."""
        return self.db.query(User).filter(
            User.tenant_id == self.tenant_id,
            User.deleted_at.is_(None)
        ).order_by(User.created_at.desc()).all()

    def update_user(self, user_id: uuid.UUID, user_in: UserUpdateByAdmin) -> User:
        """Atualiza role, is_active e/ou full_name de um Operador."""
        user = self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == self.tenant_id,
            User.deleted_at.is_(None)
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operador não encontrado."
            )
        if user_in.role is not None:
            user.role = user_in.role
        if user_in.is_active is not None:
            user.is_active = user_in.is_active
        if user_in.full_name is not None:
            user.full_name = user_in.full_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: uuid.UUID) -> None:
        """Soft delete de Operador. Nunca pode deletar a si mesmo (validado no endpoint)."""
        user = self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == self.tenant_id,
            User.deleted_at.is_(None)
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operador não encontrado."
            )
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
