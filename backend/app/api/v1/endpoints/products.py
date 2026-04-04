import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, TokenData
from app.services.product_service import ProductService

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Inspeção do Arsenal: Lista todos os produtos do estoque do Tenant."""
    service = ProductService(db, uuid.UUID(current_user.tenant_id))
    return service.list_products(skip=skip, limit=limit)

@router.post("/", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Forja de Suprimentos: Adiciona um novo SKU ao Arsenal."""
    service = ProductService(db, uuid.UUID(current_user.tenant_id))
    return service.create_product(product_in)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Visão Tática: Detalhes específicos de um item do inventário."""
    service = ProductService(db, uuid.UUID(current_user.tenant_id))
    return service.get_product(product_id)

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Refino de Arsenal: Atualiza dados de um produto (estoque, custo, etc)."""
    service = ProductService(db, uuid.UUID(current_user.tenant_id))
    return service.update_product(product_id, product_in)

@router.delete("/{product_id}")
def delete_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Expurgo de SKU: Remove um produto do inventário (Soft Delete)."""
    service = ProductService(db, uuid.UUID(current_user.tenant_id))
    service.delete_product(product_id)
    return {"message": "Item removido do Arsenal com sucesso."}
