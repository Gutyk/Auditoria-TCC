
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Document, Project, Analysis
from ..schemas import AnalysisRunIn, AnalysisOut
from ..services.analyzer import run_analysis

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/run", response_model=AnalysisOut)
def run(payload: AnalysisRunIn, db: Session = Depends(get_db)):
    if not db.query(Project).filter_by(id=payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")

    q = db.query(Document).filter_by(project_id=payload.project_id)
    if payload.document_ids:
        q = q.filter(Document.id.in_(payload.document_ids))
    docs = q.all()
    if not docs:
        raise HTTPException(status_code=400, detail="No documents to analyze")

    summary = run_analysis(d.content for d in docs)

    analysis = Analysis(project_id=payload.project_id, status="completed", summary=summary)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
