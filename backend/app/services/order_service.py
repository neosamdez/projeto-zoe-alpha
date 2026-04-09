import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, desc, case
from app.models import ServiceOrder, Lead, ServiceStatus, OrderEvent, OrderPart, Product, Technician
from app.schemas import ServiceOrderCreate, OrdersStats, TechnicianProfit
from app.schemas.order_part import OrderPartCreate
from decimal import Decimal

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

        # Busca a última OS global criada neste ano para manter a unicidade do Protocolo
        last_order = self.db.query(ServiceOrder).filter(
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
        # Base: JOIN com Lead e LEFT JOIN com Technician
        query = (
            self.db.query(
                ServiceOrder, 
                Lead.name.label("lead_name"),
                Technician.name.label("technician_name")
            )
            .join(Lead, ServiceOrder.lead_id == Lead.id)
            .outerjoin(Technician, ServiceOrder.technician_id == Technician.id)
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
        for order, lead_name, tech_name in rows:
            result.append({
                "id": order.id,
                "lead_id": order.lead_id,
                "lead_name": lead_name,
                "protocol": order.protocol,
                "status": order.status.value,
                "device_info": order.device_info,
                "technical_notes": order.technical_notes,
                "total_value": order.total_value or Decimal("0.00"),
                "parts_cost": order.parts_cost or Decimal("0.00"),
                "technician_id": order.technician_id,
                "technician": {"id": order.technician_id, "name": tech_name} if order.technician_id else None,
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

    def get_stats(self) -> OrdersStats:
        """
        [AGGREGATION CORE] Inteligência Financeira e Operacional.
        Consolida contagens e agregações de receita, custos e ranking de técnicos.
        """
        # 0. Blindagem Anti-Null (Early Return)
        total_orders_count = self.db.query(func.count(ServiceOrder.id)).filter(
            ServiceOrder.tenant_id == self.tenant_id, 
            ServiceOrder.deleted_at.is_(None)
        ).scalar() or 0

        if total_orders_count == 0:
            return OrdersStats(
                total=0,
                open=0,
                repairing=0,
                completed=0,
                projected_revenue=0.0,
                realized_revenue=0.0,
                total_parts_cost=0.0,
                realized_net_profit=0.0,
                technician_ranking=[]
            )

        # Status de Pipeline e Realizados
        PIPELINE_STATUSES = [ServiceStatus.OPEN, ServiceStatus.DIAGNOSING, ServiceStatus.AWAITING_PARTS, ServiceStatus.IN_REPAIR]
        REALIZED_STATUSES = [ServiceStatus.COMPLETED, ServiceStatus.DELIVERED]

        # 1. Contagens Básicas (usando SQLAlchemy 'case' purista)
        counts = self.db.query(
            func.sum(case((ServiceOrder.status == ServiceStatus.OPEN, 1), else_=0)).label("open"),
            func.sum(case((ServiceOrder.status == ServiceStatus.IN_REPAIR, 1), else_=0)).label("repairing"),
            func.sum(case((ServiceOrder.status == ServiceStatus.COMPLETED, 1), else_=0)).label("completed")
        ).filter(
            ServiceOrder.tenant_id == self.tenant_id, 
            ServiceOrder.deleted_at.is_(None)
        ).first()

        # 2. Agregações Monetárias
        monetary = self.db.query(
            func.sum(case((ServiceOrder.status.in_(PIPELINE_STATUSES), ServiceOrder.total_value), else_=0)).label("projected"),
            func.sum(case((ServiceOrder.status.in_(REALIZED_STATUSES), ServiceOrder.total_value), else_=0)).label("realized"),
            func.sum(ServiceOrder.parts_cost).label("total_parts_cost"),
            func.sum(case((ServiceOrder.status.in_(REALIZED_STATUSES), ServiceOrder.total_value - ServiceOrder.parts_cost), else_=0)).label("net_profit")
        ).filter(
            ServiceOrder.tenant_id == self.tenant_id, 
            ServiceOrder.deleted_at.is_(None)
        ).first()

        # 3. Ranking de Elite (Lucro por Técnico) — SPRINT 23
        ranking_query = (
            self.db.query(
                Technician.id.label("technician_id"),
                Technician.name.label("name"),
                func.sum(ServiceOrder.total_value - ServiceOrder.parts_cost).label("profit")
            )
            .join(ServiceOrder, ServiceOrder.technician_id == Technician.id)
            .filter(
                ServiceOrder.tenant_id == self.tenant_id,
                ServiceOrder.deleted_at.is_(None),
                ServiceOrder.status.in_(REALIZED_STATUSES)
            )
            .group_by(Technician.id, Technician.name)
            .order_by(desc("profit"))
            .all()
        )

        return OrdersStats(
            total=total_orders_count,
            open=int(counts.open or 0) if counts else 0,
            repairing=int(counts.repairing or 0) if counts else 0,
            completed=int(counts.completed or 0) if counts else 0,
            projected_revenue=monetary.projected or Decimal("0.0"),
            realized_revenue=monetary.realized or Decimal("0.0"),
            total_parts_cost=monetary.total_parts_cost or Decimal("0.0"),
            realized_net_profit=monetary.net_profit or Decimal("0.0"),
            technician_ranking=[
                TechnicianProfit(technician_id=r.technician_id, name=r.name, profit=r.profit or Decimal("0.0"))
                for r in ranking_query
            ]
        )

    def assign_technician(self, order_id: uuid.UUID, technician_id: uuid.UUID | None) -> ServiceOrder:
        """Atribui ou remove a responsabilidade técnica de uma Ordem de Serviço."""
        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == order_id,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

        if technician_id:
            tech = self.db.query(Technician).filter(
                Technician.id == technician_id,
                Technician.tenant_id == self.tenant_id
            ).first()
            if not tech:
                raise HTTPException(status_code=404, detail="Técnico não encontrado.")
        
        order.technician_id = technician_id
        
        # Log de Audioria
        description = f"Técnico atribuído: {tech.name}" if technician_id else "Responsabilidade técnica removida."
        event = OrderEvent(
            tenant_id=self.tenant_id,
            order_id=order_id,
            event_type="TECH_ASSIGNED",
            description=description
        )
        self.db.add(event)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def add_order_part(self, order_id: uuid.UUID, part_in: OrderPartCreate) -> OrderPart:
        """
        [Tese C] Adiciona um insumo à OS com vínculo estrito obrigatório.
        O custo total de peças na OS será atualizado usando o snapshot de custo.
        A quantidade é reservada logicamente.
        """
        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == order_id,
            ServiceOrder.tenant_id == self.tenant_id
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

        product = self.db.query(Product).filter(
            Product.id == part_in.product_id,
            Product.tenant_id == self.tenant_id,
            Product.deleted_at.is_(None)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Produto não registrado no Arsenal.")
            
        if product.current_stock - product.reserved_stock < part_in.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Estoque Insuficiente: {product.name} não possui estoque livre suficiente no arsenal."
            )

        # Incrementa o estoque reservado logicamente (Tese C)
        product.reserved_stock += part_in.quantity

        db_part = OrderPart(
            tenant_id=self.tenant_id,
            order_id=order_id,
            product_id=part_in.product_id,
            quantity=part_in.quantity,
            snapshot_cost_price=product.cost_price,
            snapshot_selling_price=product.selling_price
        )
        self.db.add(db_part)
        
        # Atualiza custo acumulado na OS (Cache tático)
        order.parts_cost = (order.parts_cost or Decimal("0.00")) + (product.cost_price * part_in.quantity)
        
        self.db.commit()
        self.db.refresh(db_part)
        return db_part

    def remove_order_part(self, part_id: uuid.UUID):
        """
        Remove um insumo e estorna logicamente o estoque reservado para o Arsenal.
        """
        part = self.db.query(OrderPart).filter(
            OrderPart.id == part_id,
            OrderPart.tenant_id == self.tenant_id
        ).first()

        if not part:
            raise HTTPException(status_code=404, detail="Insumo não encontrado.")

        # ── [ESTORNO LOGÍSTICO] ──
        product = self.db.query(Product).filter(
            Product.id == part.product_id,
            Product.tenant_id == self.tenant_id
        ).first()
        
        if product:
            product.reserved_stock -= part.quantity
            if product.reserved_stock < 0:
                product.reserved_stock = 0

        order = self.db.query(ServiceOrder).filter(
            ServiceOrder.id == part.order_id
        ).first()

        if order:
            order.parts_cost = (order.parts_cost or Decimal("0.00")) - (part.snapshot_cost_price * part.quantity)

        self.db.delete(part)
        self.db.commit()

    def get_order_parts(self, order_id: uuid.UUID) -> list[OrderPart]:
        """Lista todos os insumos vinculados a uma OS específica."""
        return self.db.query(OrderPart).filter(
            OrderPart.order_id == order_id,
            OrderPart.tenant_id == self.tenant_id
        ).all()

