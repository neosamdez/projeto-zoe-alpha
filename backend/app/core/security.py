"""
[MÓDULO: CORE SECURITY — FORTALEZA AMENTI]
Responsável por toda lógica criptográfica do sistema:
  - Hash de senha com bcrypt (passlib)
  - Geração e decodificação de JWT (python-jose)
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto de hash: bcrypt como algoritmo soberano
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


# ── FUNÇÕES DE SENHA ───────────────────────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha em texto plano com o hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano."""
    return pwd_context.hash(password)


# ── FUNÇÕES DE TOKEN JWT ────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Gera um JWT assinado com as claims fornecidas.
    - 'sub': subject (e-mail do usuário)
    - 'tenant_id': isolamento multi-tenant propagado no token
    - 'exp': expiração calculada
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um JWT.
    Retorna o payload ou None em caso de falha (expirado, assinatura inválida).
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
