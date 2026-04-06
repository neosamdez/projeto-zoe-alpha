import io
import csv
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models import ServiceOrder, OrderPart, ServiceStatus

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class ReportService:
    """
    [PROTOCOLO AMENTI: REPORT SERVICE - O REGISTRO DE GUERRA]
    Módulo tático para balanço financeiro da Cidadela. Gera artefatos blindados sem usar disco.
    """
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def get_monthly_data(self, month: int, year: int) -> dict:
        """Coleta as informações consolidadas de fechamento (Apenas COMPLETED)."""
        orders = self.db.query(ServiceOrder).filter(
            ServiceOrder.tenant_id == self.tenant_id,
            ServiceOrder.status == ServiceStatus.COMPLETED,
            ServiceOrder.deleted_at.is_(None),
            extract('month', ServiceOrder.created_at) == month,
            extract('year', ServiceOrder.created_at) == year
        ).all()
        
        total_revenue = 0.0
        total_costs = 0.0
        
        # Coleta custos de peças de forma exata e blindada via DB para cada ordem finalizada
        for order in orders:
            total_revenue += float(order.total_value or 0.0)
            
            parts_cost = self.db.query(func.sum(OrderPart.cost)).filter(
                OrderPart.order_id == order.id, 
                OrderPart.deleted_at.is_(None)
            ).scalar() or 0.0
            
            total_costs += float(parts_cost)
            
        net_profit = total_revenue - total_costs
        
        return {
            "orders": orders,
            "revenue": total_revenue,
            "costs": total_costs,
            "profit": net_profit,
            "month": month,
            "year": year
        }

    def generate_csv(self, month: int, year: int) -> io.BytesIO:
        """Forja o artefato CSV em memória (IO string stream -> bytes stream)"""
        data = self.get_monthly_data(month, year)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Protocolo", "Data Fechamento", "Status", "Receita OS (R$)", "Custos Peças (R$)", "Lucro (R$)"])
        
        for order in data["orders"]:
            parts_cost = self.db.query(func.sum(OrderPart.cost)).filter(
                OrderPart.order_id == order.id, 
                OrderPart.deleted_at.is_(None)
            ).scalar() or 0.0
            
            profit = float(order.total_value or 0) - float(parts_cost)
            writer.writerow([
                order.protocol, 
                order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                order.status.value,
                f"{float(order.total_value or 0):.2f}",
                f"{float(parts_cost):.2f}",
                f"{profit:.2f}"
            ])
            
        # Linha de Resumo
        writer.writerow([])
        writer.writerow(["RESUMO FINANCEIRO", "", "", f"{data['revenue']:.2f}", f"{data['costs']:.2f}", f"{data['profit']:.2f}"])
        
        bio = io.BytesIO(output.getvalue().encode('utf-8'))
        bio.seek(0)
        return bio
        
    def generate_pdf(self, month: int, year: int) -> io.BytesIO:
        """Forja o artefato PDF usando ReportLab (Desenho livre e seguro em memória)"""
        data = self.get_monthly_data(month, year)
        bio = io.BytesIO()
        
        c = canvas.Canvas(bio, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        
        c.drawString(50, height - 70, "IMPÉRIO ASI - REGISTRO DE GUERRA")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Período de Referência: {month:02d}/{year}")
        c.drawString(50, height - 120, f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC")
        
        # Resumo Financeiro
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 160, "RESUMO FINANCEIRO")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 180, f"Receita Bruta Total: R$ {data['revenue']:.2f}")
        c.drawString(50, height - 200, f"Custos de Arsenal: R$ {data['costs']:.2f}")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 220, f"LUCRO LÍQUIDO REAL: R$ {data['profit']:.2f}")
        
        # Tabela (Cabeçalho)
        y = height - 270
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "PROTOCOLO")
        c.drawString(160, y, "DATA")
        c.drawString(280, y, "RECEITA")
        c.drawString(380, y, "CUSTOS")
        c.drawString(480, y, "LUCRO")
        
        c.setFont("Helvetica", 10)
        y -= 25
        
        # Linhas das Ordens
        for order in data["orders"]:
            if y < 60:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 10)
                
            parts_cost = self.db.query(func.sum(OrderPart.cost)).filter(
                OrderPart.order_id == order.id, 
                OrderPart.deleted_at.is_(None)
            ).scalar() or 0.0
            profit = float(order.total_value or 0) - float(parts_cost)
            
            c.drawString(50, y, str(order.protocol))
            c.drawString(160, y, order.created_at.strftime("%d/%m/%Y"))
            c.drawString(280, y, f"R$ {float(order.total_value or 0):.2f}")
            c.drawString(380, y, f"R$ {float(parts_cost):.2f}")
            c.drawString(480, y, f"R$ {profit:.2f}")
            y -= 20
            
        c.save()
        bio.seek(0)
        return bio
