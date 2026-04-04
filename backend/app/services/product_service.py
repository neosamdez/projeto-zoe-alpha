import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate

class ProductService:
    """
    [PROTOCOLO AMENTI: PRODUCT SERVICE]
    Camada de inteligência para o Arsenal de Elite.
    Garante isolamento multi-tenant e integridade física do estoque.
    """
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def list_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Recupera o arsenal completo do Tenant."""
        return self.db.query(Product).filter(
            Product.tenant_id == self.tenant_id,
            Product.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    def get_product(self, product_id: uuid.UUID) -> Product:
        """Busca um item específico no inventário."""
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.tenant_id == self.tenant_id,
            Product.deleted_at.is_(None)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Item não encontrado no Arsenal.")
        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        """Forja um novo SKU no inventário."""
        
        # Trava de SKU Duplicado por Tenant
        existing = self.db.query(Product).filter(
            Product.sku == product_in.sku,
            Product.tenant_id == self.tenant_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"O SKU {product_in.sku} já existe na Cidadela.")

        db_product = Product(
            tenant_id=self.tenant_id,
            **product_in.model_dump()
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update_product(self, product_id: uuid.UUID, product_in: ProductUpdate) -> Product:
        """Refina os dados de um item do arsenal."""
        db_product = self.get_product(product_id)
        
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
            
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: uuid.UUID):
        """Remove um item do arsenal (Soft Delete)."""
        db_product = self.get_product(product_id)
        
        from datetime import datetime, timezone
        db_product.deleted_at = datetime.now(timezone.utc)
        
        self.db.commit()
