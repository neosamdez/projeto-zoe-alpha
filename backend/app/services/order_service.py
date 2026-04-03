import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models import ServiceOrder, Lead, ServiceStatus
from app.schemas import ServiceOrderCreate

class OrderService:
    """
    Camada Exclusiva de Processamento de Negócio para entidade ServiceOrder.
    """
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def generate_protocol(self) -> str:
        """
        Gera o protocolo sequencial no padrão ASI-YY-XXXX.
        Reseta a cada ano.
        """
        current_year = datetime.now(timezone.utc).year
        year_suffix = str(current_year)[-2:]

        # Busca a última OS criada neste ano
        last_order = self.db.query(ServiceOrder).filter(
            ServiceOrder.tenant_id == self.tenant_id,
            extract('year', ServiceOrder.created_at) == current_year
        ).order_by(ServiceOrder.created_at.desc()).first()

        if not last_order or not last_order.protocol.startswith(f"ASI-{year_suffix}-"):
            new_sequence = 1
        else:
            # Extrai o numero do protocolo ASI-YY-XXXX
            try:
                last_sequence_str = last_order.protocol.split('-')[2]
                new_sequence = int(last_sequence_str) + 1
            except (IndexError, ValueError):
                new_sequence = 1

        return f"ASI-{year_suffix}-{new_sequence:04d}"

    def create_order_from_lead(self, lead_id: uuid.UUID, order_in: ServiceOrderCreate) -> ServiceOrder:
        """Processo Estrito de Criação de OS a partir de Lead."""
        
        # 1. Validar se o Lead existe e pertence ao tenant
        lead = self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.tenant_id == self.tenant_id
        ).first()

        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado para o Tenant ativo.")

        # 2. Trava de Duplicidade
        existing_order = self.db.query(ServiceOrder).filter(
            ServiceOrder.lead_id == lead_id,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if existing_order:
            raise HTTPException(
                status_code=400, 
                detail="Operação Invalida: Este Lead já possui uma Ordem de Serviço vinculada."
            )

        # 3. Gerador de Protocolo
        protocol = self.generate_protocol()

        # 4. Injeção de Banco
        db_order = ServiceOrder(
            tenant_id=self.tenant_id,
            lead_id=lead.id,
            protocol=protocol,
            status=ServiceStatus.OPEN,
            device_info=order_in.device_info,
            technical_notes=order_in.technical_notes,
            total_value=0.00
        )
        
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: str = None,
        search_query: str = None,
    ):
        """
        Lista Ordens do Tenant com JOIN em Lead para retornar lead_name.

        Hotfix Sprint 14:
        - Sempre faz JOIN com Lead (elimina N+1 queries)
        - Injeta _lead_name no objeto ServiceOrder (lido pelo model_validate do schema)
        - Aplica ilike em protocol, device_info e Lead.name se search_query fornecido
        """
        # Base: JOIN com Lead para capturar o nome do cliente em uma única query
        query = (
            self.db.query(ServiceOrder, Lead.name.label("lead_name"))
            .join(Lead, ServiceOrder.lead_id == Lead.id)
            .filter(
                ServiceOrder.tenant_id == self.tenant_id,
                ServiceOrder.deleted_at.is_(None),
            )
        )

        # Filtro de status (opcional)
        if status_filter:
            query = query.filter(ServiceOrder.status == status_filter)

        # Busca global (opcional) — ilike em 3 campos
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                func.lower(ServiceOrder.protocol).ilike(term) |
                func.lower(ServiceOrder.device_info).ilike(term) |
                func.lower(Lead.name).ilike(term)
            )

        rows = query.order_by(ServiceOrder.created_at.desc()).offset(skip).limit(limit).all()

        # Injeta _lead_name como atributo dinâmico no objeto ORM
        # O model_validate do ServiceOrderResponse lê este atributo
        for order, lead_name in rows:
            object.__setattr__(order, '_lead_name', lead_name)

        return [order for order, _ in rows]

    def get_order_by_protocol(self, protocol: str) -> ServiceOrder:
        """Busca detalhada usando protocolo e validando dono (tenant_id)."""
        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.protocol == protocol,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Ordem de Serviço protegida ou não encontrada.")
            
        return order

    def update_order_status(self, order_id: uuid.UUID, new_status: ServiceStatus) -> ServiceOrder:
        """Atualiza a Ordem de Serviço garantindo que o Tenant é o dono e revalida os estagios."""
        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == order_id,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Ordem de Serviço protegida ou não encontrada.")

        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

