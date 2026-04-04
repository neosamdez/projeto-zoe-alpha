import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models import ServiceOrder, Lead, ServiceStatus, OrderEvent, OrderPart
from app.schemas import ServiceOrderCreate, OrderPartCreate

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
        self.db.flush() # Para pegar o ID da OS recém-criada

        # [LOG DE AUDITORIA] Registro de Abertura
        event = OrderEvent(
            tenant_id=self.tenant_id,
            order_id=db_order.id,
            event_type="CREATED",
            description=f"Ordem de Serviço forjada com protocolo {protocol}."
        )
        self.db.add(event)

        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: str = None,
        search_query: str = None,
    ) -> list[dict]:
        """
        Lista Ordens do Tenant com JOIN em Lead.

        Sprint 15 Fix — Pipeline de Dados Correto:
        Retorna lista de dicts explícitos (NÃO objetos ORM).
        Isso garante que `lead_name` chegue corretamente ao Pydantic/JSON,
        sem depender de injeção frágil de atributo em instâncias SQLAlchemy.

        Fluxo:
          SQL JOIN (ServiceOrder + Lead) → tuple (order, lead_name)
          → dict com todos os campos → Pydantic valida → JSON com lead_name
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

        # Constrói dicts explícitos: Pydantic lê diretamente sem magia de ORM
        result = []
        for order, lead_name in rows:
            result.append({
                "id": order.id,
                "lead_id": order.lead_id,
                "lead_name": lead_name,           # ← chave garantida no JSON
                "protocol": order.protocol,
                "status": order.status.value,     # ← enum → string aqui, não no Pydantic
                "device_info": order.device_info,
                "technical_notes": order.technical_notes,
                "total_value": float(order.total_value or 0),
                "parts_cost": float(order.parts_cost or 0),
                "created_at": order.created_at,
            })

        return result


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

        old_status = order.status.value
        order.status = new_status

        # [LOG DE AUDITORIA] Registro de Mudança de Estágio
        event = OrderEvent(
            tenant_id=self.tenant_id,
            order_id=order.id,
            event_type="STATUS_CHANGED",
            description=f"Status alterado de {old_status} para {new_status.value}."
        )
        self.db.add(event)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_events(self, order_id: uuid.UUID) -> list[OrderEvent]:
        """Recupera a linha do tempo cronológica de uma Ordem de Serviço."""
        return self.db.query(OrderEvent).filter(
            OrderEvent.order_id == order_id,
            OrderEvent.tenant_id == self.tenant_id
        ).order_by(OrderEvent.created_at.desc()).all()

    def get_analytics(self, days: int = 30) -> dict:
        """
        Gera dados de Volume (temporal) e Distribuição (por status).
        Sprint 20 — O Reator ARC.
        """
        from datetime import timedelta
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # 1. Volume por Dia (Últimos X dias)
        volume_query = (
            self.db.query(
                func.date(ServiceOrder.created_at).label("date"),
                func.count(ServiceOrder.id).label("count")
            )
            .filter(
                ServiceOrder.tenant_id == self.tenant_id,
                ServiceOrder.created_at >= start_date,
                ServiceOrder.deleted_at.is_(None)
            )
            .group_by(func.date(ServiceOrder.created_at))
            .order_by(func.date(ServiceOrder.created_at))
            .all()
        )

        # 2. Distribuição por Status
        distribution_query = (
            self.db.query(
                ServiceOrder.status,
                func.count(ServiceOrder.id).label("count")
            )
            .filter(
                ServiceOrder.tenant_id == self.tenant_id,
                ServiceOrder.deleted_at.is_(None)
            )
            .group_by(ServiceOrder.status)
            .all()
        )

        return {
            "volume": [{"date": str(d), "count": c} for d, c in volume_query],
            "distribution": [{"status": s.value, "count": c} for s, c in distribution_query]
        }

    def add_order_part(self, order_id: uuid.UUID, part_in: OrderPartCreate) -> OrderPart:
        """Adiciona um insumo à OS e atualiza o custo total de peças."""
        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == order_id,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

        db_part = OrderPart(
            tenant_id=self.tenant_id,
            order_id=order_id,
            description=part_in.description,
            cost=part_in.cost
        )
        self.db.add(db_part)
        
        # Atualiza custo acumulado na OS (Cache tático)
        order.parts_cost = float(order.parts_cost or 0) + float(part_in.cost)
        
        self.db.commit()
        self.db.refresh(db_part)
        return db_part

    def remove_order_part(self, part_id: uuid.UUID):
        """Remove um insumo e abate o valor do custo total da OS."""
        part = self.db.query(OrderPart).filter(
            OrderPart.id == part_id,
            OrderPart.tenant_id == self.tenant_id
        ).first()

        if not part:
            raise HTTPException(status_code=404, detail="Insumo não encontrado.")

        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == part.order_id
        ).first()

        if order:
            order.parts_cost = float(order.parts_cost or 0) - float(part.cost)

        self.db.delete(part)
        self.db.commit()

    def get_order_parts(self, order_id: uuid.UUID) -> list[OrderPart]:
        """Lista todos os insumos vinculados a uma OS específica."""
        return self.db.query(OrderPart).filter(
            OrderPart.order_id == order_id,
            OrderPart.tenant_id == self.tenant_id
        ).all()

