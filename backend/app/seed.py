"""
[SEED: POPULAÇÃO INICIAL DA CIDADELA]
Script standalone para popular o banco com dados de teste.
Execução: docker compose exec api python -m app.seed
"""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.database import SessionLocal
from app.models import User, UserRole, Lead, ServiceOrder, ServiceStatus, OrderEvent, OrderPart, Product, Technician, DefectCode
from app.core.security import get_password_hash

TENANT_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")


def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@amenti.io").first()
        if existing:
            print("[SEED] Banco já possui dados. Abortando.")
            return

        print("[SEED] Forjando dados da Cidadela...")

        # ── 1. ADMIN ──────────────────────────────────────────────────────────
        admin = User(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            full_name="Comandante Amenti",
            email="admin@amenti.io",
            hashed_password=get_password_hash("amenti2026"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)

        # ── 2. TÉCNICOS ───────────────────────────────────────────────────────
        tech_data = [
            ("Carlos Mendes", "Notebook & MacBook"),
            ("Mariana Silva", "iPhone & iPad"),
            ("Rafael Costa", "Android & Samsung"),
        ]
        technicians = []
        for name, spec in tech_data:
            tech = Technician(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                name=name,
                specialization=spec,
                is_active=True,
            )
            db.add(tech)
            technicians.append(tech)

        db.flush()

        # ── 3. LEADS ──────────────────────────────────────────────────────────
        lead_data = [
            ("João Pedro Almeida", "joao@email.com", "11988001001", "MacBook Pro M2", "Tela com linhas verticais"),
            ("Ana Carolina Souza", "ana.souza@email.com", "11988001002", "iPhone 14 Pro", "Bateria drenando rápido"),
            ("Lucas Ferreira", "lucas.f@email.com", "11988001003", "Samsung Galaxy S23", "Conector de carga solto"),
            ("Maria Eduarda Lima", "maria.lima@email.com", "11988001004", "iPad Air 5", "Tela trincada"),
            ("Pedro Henrique Rocha", "pedro.r@email.com", "11988001005", "Dell XPS 15", "Não liga após queda"),
        ]
        leads = []
        for name, email, phone, device, notes in lead_data:
            lead = Lead(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                name=name,
                email=email,
                phone=phone,
                device_interest=device,
                notes=notes,
            )
            db.add(lead)
            leads.append(lead)

        db.flush()

        # ── 4. PRODUTOS ───────────────────────────────────────────────────────
        product_data = [
            ("Tela iPhone 14 Pro OEM", "TLA-I14P-OEM", Decimal("450.00"), Decimal("890.00"), 8, 2),
            ("Bateria MacBook Pro M2", "BAT-MBP-M2", Decimal("320.00"), Decimal("680.00"), 5, 1),
            ("Conector USB-C Samsung S23", "CNC-SS23-UC", Decimal("45.00"), Decimal("120.00"), 15, 3),
            ("Tela iPad Air 5 Compatível", "TLA-IPA5-CMP", Decimal("380.00"), Decimal("750.00"), 4, 1),
            ("Fonte Dell XPS 15 130W", "FNT-XPS15-130", Decimal("180.00"), Decimal("420.00"), 6, 2),
        ]
        products = []
        for name, sku, cost, sell, stock, min_s in product_data:
            prod = Product(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                name=name,
                sku=sku,
                cost_price=cost,
                selling_price=sell,
                current_stock=stock,
                reserved_stock=0,
                min_stock=min_s,
            )
            db.add(prod)
            products.append(prod)

        db.flush()

        # ── 5. ORDENS DE SERVIÇO ──────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        order_configs = [
            (leads[0], "MacBook Pro M2 2023 — Linhas verticais na tela", "Possível dano no flex da tela. Diagnóstico inicial: backlight ok, LCD com artefatos.", ServiceStatus.OPEN, None, Decimal("0.00"), now - timedelta(hours=2)),
            (leads[1], "iPhone 14 Pro — Bateria drenando em 2h", "Cycle count: 892. Capacidade: 58%. Substituição recomendada.", ServiceStatus.DIAGNOSING, technicians[1], Decimal("0.00"), now - timedelta(hours=8)),
            (leads[2], "Samsung Galaxy S23 — Conector de carga instável", "Conector USB-C com folga. Necessária substituição do conector.", ServiceStatus.AWAITING_PARTS, technicians[2], Decimal("0.00"), now - timedelta(days=1)),
            (leads[3], "iPad Air 5 — Tela trincada no canto superior direito", "Tela LCD intacta, apenas glass frontal trincado. Touch funcional.", ServiceStatus.IN_REPAIR, technicians[0], Decimal("750.00"), now - timedelta(days=3)),
            (leads[4], "Dell XPS 15 9520 — Não liga após queda de 50cm", "Sem sinal de vida. LED de power pisca 3x (código: falha na fonte).", ServiceStatus.COMPLETED, technicians[0], Decimal("420.00"), now - timedelta(days=7)),
        ]

        orders = []
        for i, (lead, device_info, tech_notes, status, tech, total_val, created) in enumerate(order_configs):
            protocol = f"ASI-26-{i + 1:04d}"
            order = ServiceOrder(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                lead_id=lead.id,
                protocol=protocol,
                status=status,
                device_info=device_info,
                technical_notes=tech_notes,
                total_value=total_val,
                parts_cost=Decimal("0.00"),
                technician_id=tech.id if tech else None,
                created_at=created,
            )
            db.add(order)
            orders.append(order)

        db.flush()

        # ── 6. ORDER EVENTS ───────────────────────────────────────────────────
        for order in orders:
            event = OrderEvent(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                order_id=order.id,
                event_type="CREATED",
                description=f"Ordem de Serviço forjada com protocolo {order.protocol}.",
                created_at=order.created_at,
            )
            db.add(event)

        for order in orders:
            if order.status != ServiceStatus.OPEN and order.status != ServiceStatus.CANCELED:
                event = OrderEvent(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    order_id=order.id,
                    event_type="STATUS_CHANGED",
                    description=f"Status alterado de OPEN para {order.status.value}.",
                    created_at=order.created_at + timedelta(hours=1),
                )
                db.add(event)

        for order in orders:
            if order.technician_id:
                tech_name = next((t.name for t in technicians if t.id == order.technician_id), "Desconhecido")
                event = OrderEvent(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    order_id=order.id,
                    event_type="TECH_ASSIGNED",
                    description=f"Técnico atribuído: {tech_name}",
                    created_at=order.created_at + timedelta(minutes=30),
                )
                db.add(event)

        # ── 7. ORDER PARTS (insumos em OS completas/em reparo) ────────────────
        parts_assignments = [
            (orders[3], products[3], 1),
            (orders[4], products[4], 1),
            (orders[4], products[2], 2),
        ]
        for order, product, qty in parts_assignments:
            part = OrderPart(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                snapshot_cost_price=product.cost_price,
                snapshot_selling_price=product.selling_price,
            )
            db.add(part)

            product.reserved_stock += qty
            order.parts_cost = (order.parts_cost or Decimal("0.00")) + (product.cost_price * qty)

    # Recalcular total_value para OS com parts
    orders[3].total_value = Decimal("750.00")
    orders[4].total_value = Decimal("420.00") + (products[4].selling_price - products[4].cost_price) + ((products[2].selling_price - products[2].cost_price) * 2)

    # ── 8. DEFECT CODES (Sprint 28 — Catálogo Samsung SR01-SR22) ─────────
    defect_data = [
        ("SR01", "Oxidação / Corrosão", "COMUM", "Comum"),
        ("SR02", "Não Liga", "COMUM", "Comum"),
        ("SR03", "Inutilizado (Reason 807)", "COMUM", None),
        ("SR04", "Ruído / Interferência imagem/som", "COMUM", "Comum"),
        ("SR05", "Sem Áudio / Volume baixo", "COMUM", "Comum"),
        ("SR06", "Desliga Sozinho / Liga e Desliga", "COMUM", "Comum"),
        ("SR07", "Fuga de Corrente", "HA_AC", "HA/AC"),
        ("SR08", "Defeitos na Imagem / Mancha na Tela / Linhas", "PAINEL", "Painel/OCTA"),
        ("SR09", "Sem Imagem / Luz de fundo apagada", "PAINEL", "Painel/OCTA"),
        ("SR10", "Touch não Funciona / Botões / Teclas", "PAINEL", "Painel/OCTA/PBA"),
        ("SR11", "Não Escreve IMEI / Não atualiza SW", "PBA", "PBA"),
        ("SR12", "Travando / Lento / Não Sintoniza", "COMUM", "Comum"),
        ("SR13", "Não Carrega", "BATERIA", "Bateria"),
        ("SR14", "Não Segura Carga", "BATERIA", "Bateria"),
        ("SR15", "Bateria Estufada", "BATERIA", "Bateria"),
        ("SR16", "Baixa Compressão", "HA_AC", "HA/AC"),
        ("SR17", "Erros de IPM / DC link", "HA_AC", "HA/AC"),
        ("SR18", "Não Reconhece SIM Card", "HHP", "HHP"),
        ("SR19", "Não faz Chamada", "HHP", "HHP"),
        ("SR20", "Wi-Fi / BT / GPS", "HHP", "HHP"),
        ("SR21", "Câmera com Problema", "HHP", "HHP/NPC"),
        ("SR22", "Outros / Não reconhece HDMI", "COMUM", "Comum/PBA"),
    ]
    for code, desc, cat, part in defect_data:
        dc = DefectCode(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            code=code,
            description=desc,
            category=cat,
            most_used_part=part,
            is_active=True,
        )
        db.add(dc)

    db.commit()
    print("[SEED] ✅ Cidadela populada com sucesso!")
    print(f" - 1 Admin (admin@amenti.io / amenti2026)")
    print(f" - {len(technicians)} Técnicos")
    print(f" - {len(leads)} Leads")
    print(f" - {len(products)} Produtos")
    print(f" - {len(orders)} Ordens de Serviço")
    print(f" - Events + Parts vinculados")
    print(f" - {len(defect_data)} Códigos de Defeito (SR01-SR22)")

    except Exception as e:
        db.rollback()
        print(f"[SEED] ❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
