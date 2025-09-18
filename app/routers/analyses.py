# backend/app/routers/analyses.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Project, Document
from ..schemas import AnalysisRunIn, AnalysisDocResult
from ..services.analyses import analyze_document

router = APIRouter(prefix="/analyses", tags=["analyses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/run", response_model=List[AnalysisDocResult])
def run_analysis(payload: AnalysisRunIn, db: Session = Depends(get_db)):
    project = db.query(Project).filter_by(id=payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    q = db.query(Document).filter_by(project_id=payload.project_id)
    if payload.document_ids:
        q = q.filter(Document.id.in_(payload.document_ids))
    docs = q.order_by(Document.id.desc()).all()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents to analyze")

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
            "created_at": d.created_at,
            "result": result,
        })
    return results
