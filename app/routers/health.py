"""
Health check endpoints para HubPDF
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check básico da API
    """
    return JSONResponse({
        "status": "ok",
        "service": "HubPDF API"
    })

@router.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Health check da conexão com o banco de dados
    Testa se consegue executar query no Postgres
    """
    try:
        # Executar query simples para verificar conexão
        result = db.execute(text("SELECT 1 AS ok")).first()
        
        if result and result[0] == 1:
            # Verificar se tabela users existe
            users_check = db.execute(
                text("SELECT COUNT(*) FROM users")
            ).first()
            
            return JSONResponse({
                "status": "ok",
                "database": "connected",
                "type": "PostgreSQL (Neon)",
                "users_count": users_check[0] if users_check else 0
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database query failed"
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "disconnected",
                "error": str(e)
            }
        )
