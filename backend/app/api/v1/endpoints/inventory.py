import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_inventory_service
from app.models import User
from app.services.inventory_service import InventoryService
from app.schemas.inventory import InventoryMovementCreate, InventoryMovementResponse, InventoryDashboard
from app.schemas.product import ProductResponse


router = APIRouter()


@router.get("/dashboard", response_model=InventoryDashboard, summary="Dashboard de Inventário")
def get_inventory_dashboard(
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_dashboard()


@router.get("/low-stock", response_model=List[ProductResponse], summary="Produtos com Estoque Baixo")
def list_low_stock(
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_low_stock()


@router.get("/movements", response_model=List[InventoryMovementResponse], summary="Listar Movimentações")
def list_movements(
    product_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_movements(product_id=product_id, skip=skip, limit=limit)


@router.post("/movements", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED, summary="Registrar Movimentação")
def create_movement(
    data: InventoryMovementCreate,
    background_tasks: BackgroundTasks,
    service: InventoryService = Depends(get_inventory_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_movement(user_id=current_user.id, data=data, background_tasks=background_tasks)

