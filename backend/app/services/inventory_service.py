import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import InventoryMovement, Product, MovementType
from app.schemas.inventory import InventoryMovementCreate, InventoryDashboard
from app.core.cache import cache_get, cache_set, cache_invalidate
from fastapi import HTTPException, BackgroundTasks
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, db: Session, tenant_id: uuid.UUID, alert_service=None):
        self.db = db
        self.tenant_id = tenant_id
        self.alert_service = alert_service

    def list_movements(self, product_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 50) -> List[InventoryMovement]:
        q = self.db.query(InventoryMovement).filter(InventoryMovement.tenant_id == self.tenant_id, InventoryMovement.deleted_at.is_(None))
        if product_id:
            q = q.filter(InventoryMovement.product_id == product_id)
        return q.order_by(desc(InventoryMovement.created_at)).offset(skip).limit(limit).all()

    def get_product_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id, Product.tenant_id == self.tenant_id).first()

    def get_critical_stock_products(self) -> List[Product]:
        return self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id,
            Product.deleted_at.is_(None),
            Product.current_stock <= Product.min_stock,
        ).all()

    def create_movement(self, user_id: uuid.UUID, data: InventoryMovementCreate, background_tasks: BackgroundTasks = None) -> InventoryMovement:
        product = self.db.query(Product).filter(Product.id == data.product_id, Product.tenant_id == self.tenant_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        movement = InventoryMovement(
            tenant_id=self.tenant_id,
            product_id=data.product_id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            reference_id=data.reference_id,
            notes=data.notes,
            created_by=user_id,
        )
        self.db.add(movement)

        if data.movement_type == MovementType.IN:
            product.current_stock += data.quantity
        elif data.movement_type == MovementType.OUT:
            product.current_stock = max(0, product.current_stock - data.quantity)
        elif data.movement_type == MovementType.RESERVE:
            product.reserved_stock += data.quantity
        elif data.movement_type == MovementType.RELEASE:
            product.reserved_stock = max(0, product.reserved_stock - data.quantity)
        elif data.movement_type == MovementType.RETURN:
            product.current_stock += data.quantity
        elif data.movement_type == MovementType.DISCARD:
            product.current_stock = max(0, product.current_stock - data.quantity)

        self.db.commit()
        self.db.refresh(movement)

        if self.alert_service and background_tasks:
            try:
                background_tasks.add_task(self.alert_service.check_and_notify_low_stock, product.id)
            except Exception as e:
                logger.error(f"Failed to schedule alert: {e}")

        cache_invalidate(f"inventory_dashboard:{self.tenant_id}")
        return movement

    def get_dashboard(self) -> InventoryDashboard:
        cache_key = f"inventory_dashboard:{self.tenant_id}"
        cached = cache_get(cache_key)
        if cached:
            return InventoryDashboard(**cached)

        products = self.db.query(Product).filter(Product.tenant_id == self.tenant_id, Product.deleted_at.is_(None)).all()
        total_products = len(products)
        total_stock = sum(p.current_stock for p in products)
        total_reserved = sum(p.reserved_stock for p in products)
        low_stock_count = sum(1 for p in products if p.current_stock <= p.min_stock)
        result = InventoryDashboard(
            total_products=total_products,
            total_stock=total_stock,
            total_reserved=total_reserved,
            total_available=total_stock - total_reserved,
            low_stock_count=low_stock_count,
        )
        cache_set(cache_key, result.model_dump(), ttl=120)
        return result

    def list_low_stock(self) -> List[Product]:
        return self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id,
            Product.deleted_at.is_(None),
            Product.current_stock <= Product.min_stock,
        ).all()
