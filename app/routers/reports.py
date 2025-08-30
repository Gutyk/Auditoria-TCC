
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Analysis
from ..schemas import AnalysisOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_report(analysis_id: int, db: Session = Depends(get_db)):
    a = db.query(Analysis).filter_by(id=analysis_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return a
