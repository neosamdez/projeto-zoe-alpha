import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models import User
from app.database import get_db
from app.api.dependencies import get_current_user
from app.services.report_service import ReportService

router = APIRouter()

@router.get(
    "/monthly",
    summary="Exportar Histórico Financeiro Mensal (Registro de Guerra)",
    description="Gera o dossiê da Cidadela em formato PDF ou CSV. Totalmente gerado em memória (Zero I/O disk) e restrito logicamente pelo Tenant ativo."
)
def get_monthly_report(
    month: int = Query(..., description="Mês de referência (1-12)"),
    year: int = Query(..., description="Ano do exercício"),
    format: str = Query("pdf", description="Formato desejado ('pdf', 'csv', ou 'json')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ReportService(db=db, tenant_id=current_user.tenant_id)
    
    if format.lower() == "csv":
        bio = service.generate_csv(month, year)
        return StreamingResponse(
            bio, 
            media_type="text/csv", 
            headers={
                "Content-Disposition": f"attachment; filename=Registro_Guerra_{year}_{month:02d}.csv"
            }
        )
    elif format.lower() == "pdf":
        bio = service.generate_pdf(month, year)
        return StreamingResponse(
            bio, 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": f"inline; filename=Registro_Guerra_{year}_{month:02d}.pdf"
            }
        )
    elif format.lower() == "json":
        data = service.get_monthly_data(month, year)
        return {
            "revenue": data["revenue"],
            "costs": data["costs"],
            "profit": data["profit"],
            "month": data["month"],
            "year": data["year"]
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail="Formato inválido. O Trono aceita apenas 'pdf', 'csv' ou 'json'."
        )
