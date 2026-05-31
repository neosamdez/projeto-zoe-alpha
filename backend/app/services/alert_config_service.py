import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import AlertConfig
from app.schemas.alert_config import AlertConfigCreate, AlertConfigUpdate
from app.core.cache import cache_get, cache_set, cache_invalidate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class AlertConfigService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def list_configs(self, skip: int = 0, limit: int = 50) -> List[AlertConfig]:
        return (
            self.db.query(AlertConfig)
            .filter(AlertConfig.tenant_id == self.tenant_id, AlertConfig.deleted_at.is_(None))
            .order_by(AlertConfig.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_config(self, config_id: uuid.UUID) -> Optional[AlertConfig]:
        return (
            self.db.query(AlertConfig)
            .filter(AlertConfig.id == config_id, AlertConfig.tenant_id == self.tenant_id, AlertConfig.deleted_at.is_(None))
            .first()
        )

    def create_config(self, data: AlertConfigCreate) -> AlertConfig:
        existing = (
            self.db.query(AlertConfig)
            .filter(AlertConfig.tenant_id == self.tenant_id, AlertConfig.name == data.name, AlertConfig.deleted_at.is_(None))
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Já existe uma configuração com este nome.")

        config = AlertConfig(
            tenant_id=self.tenant_id,
            name=data.name,
            recipient_email=data.recipient_email,
            is_active=data.is_active,
            min_stock_threshold=data.min_stock_threshold,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)

        cache_invalidate(f"alert_configs:{self.tenant_id}")
        logger.info(f"AlertConfig criada: {config.name} ({config.id})")
        return config

    def update_config(self, config_id: uuid.UUID, data: AlertConfigUpdate) -> AlertConfig:
        config = self.get_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuração não encontrada.")

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != config.name:
            existing = (
                self.db.query(AlertConfig)
                .filter(AlertConfig.tenant_id == self.tenant_id, AlertConfig.name == update_data["name"], AlertConfig.deleted_at.is_(None))
                .first()
            )
            if existing:
                raise HTTPException(status_code=409, detail="Já existe uma configuração com este nome.")

        for key, value in update_data.items():
            setattr(config, key, value)

        self.db.commit()
        self.db.refresh(config)

        cache_invalidate(f"alert_configs:{self.tenant_id}")
        logger.info(f"AlertConfig atualizada: {config.name} ({config.id})")
        return config

    def delete_config(self, config_id: uuid.UUID) -> bool:
        from datetime import datetime, timezone
        config = self.get_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuração não encontrada.")

        config.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

        cache_invalidate(f"alert_configs:{self.tenant_id}")
        logger.info(f"AlertConfig removida: {config.name} ({config.id})")
        return True

    def get_active_recipients(self, threshold: int = 0) -> List[str]:
        cache_key = f"alert_configs:{self.tenant_id}"
        cached = cache_get(cache_key)
        if cached:
            return [r for r in cached if threshold >= 0]

        configs = (
            self.db.query(AlertConfig)
            .filter(AlertConfig.tenant_id == self.tenant_id, AlertConfig.is_active == True, AlertConfig.deleted_at.is_(None))
            .all()
        )
        recipients = [c.recipient_email for c in configs if c.min_stock_threshold <= threshold or c.min_stock_threshold == 0]
        return recipients
