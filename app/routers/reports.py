# backend/app/routers/reports.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project, Document
from ..schemas import AnalysisDocResult
from app.services.analyses import analyze_document

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{project_id}", response_model=List[AnalysisDocResult])
def get_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    docs = (
        db.query(Document)
        .filter_by(project_id=project_id)
        .order_by(Document.id.desc())
        .all()
    )
    if not docs:
        raise HTTPException(status_code=404, detail="No documents for this project")

    results: List[AnalysisDocResult] = []
    for d in docs:
        result = analyze_document({
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "created_at": d.created_at,
        })
        results.append({
            "document_id": d.id,
            "title": d.title,
            "created_at": d.created_at,  # pydantic converte automaticamente para ISO 8601
            "result": result
        })
    return results
