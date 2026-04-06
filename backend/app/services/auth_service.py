"""
[SERVIÇO: AUTH SERVICE — CAMADA DE NEGÓCIO]
Lógica de autenticação e gestão de utilizadores.
Princípio Amenti: regras de negócio vivem no Service, nunca no Controller.
"""
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate
from app.core.security import get_password_hash, verify_password


class AuthService:
    def __init__(self, db: Session, tenant_id: uuid.UUID = None):
        self.db = db
        self.tenant_id = tenant_id

    def register_user(self, user_in: UserCreate) -> User:
        """
        Registra um novo Operador.
        Trava de duplicidade: e-mail único globalmente.
        Se não houver tenant_id vinculado (Módulo Público), forja uma nova Cidadela (Tenant).
        """
        existing = (
            self.db.query(User)
            .filter(User.email == user_in.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"E-mail '{user_in.email}' já possui registro na Matrix."
            )

        final_tenant_id = self.tenant_id or uuid.uuid4()

        new_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
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
