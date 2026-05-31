import logging
from app.services.email_service import EmailService
from app.services.alert_config_service import AlertConfigService
from app.models import Product
from app.core.config import settings
from sqlalchemy.orm import Session
import uuid

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db: Session, email_service: EmailService, tenant_id: uuid.UUID = None):
        self.db = db
        self.email_service = email_service
        self.tenant_id = tenant_id

    def check_and_notify_low_stock(self, product_id: uuid.UUID):
        try:
            product = self.db.query(Product).filter(
                Product.id == product_id,
                Product.deleted_at.is_(None)
            ).first()

            if product and product.current_stock <= product.min_stock:
                subject = f"ALERTA: Estoque Baixo - {product.name}"
                body = f"O produto {product.name} atingiu o nível crítico: {product.current_stock} unidades (mínimo: {product.min_stock})."

                recipients = []
                if self.tenant_id:
                    config_service = AlertConfigService(db=self.db, tenant_id=self.tenant_id)
                    recipients = config_service.get_active_recipients(threshold=product.current_stock)

                if not recipients:
                    recipients = [settings.ADMIN_EMAIL]

                for recipient in recipients:
                    logger.info(f"Disparando alerta de estoque para {product.name} -> {recipient}")
                    self.email_service.send_alert(recipient, subject, body)
        except Exception as e:
            logger.error(f"Falha no AlertService: {str(e)}")

    def process_alerts_batch(self, tenant_id: uuid.UUID = None):
        effective_tenant_id = tenant_id or self.tenant_id
        q = self.db.query(Product).filter(Product.deleted_at.is_(None))
        if effective_tenant_id:
            q = q.filter(Product.tenant_id == effective_tenant_id)
        critical_products = q.filter(Product.current_stock <= Product.min_stock).all()

        for product in critical_products:
            if not self.tenant_id and product.tenant_id:
                self.tenant_id = product.tenant_id
            self.check_and_notify_low_stock(product.id)
