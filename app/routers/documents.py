
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Document, Project
from ..schemas import DocumentIn, DocumentOut
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=DocumentOut)
def create_document(payload: DocumentIn, db: Session = Depends(get_db)):
    if not db.query(Project).filter_by(id=payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    d = Document(project_id=payload.project_id, title=payload.title, content=payload.content)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@router.get("/{project_id}", response_model=List[DocumentOut])
def list_documents(project_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter_by(project_id=project_id).all()
    return [DocumentOut.model_validate(doc) for doc in docs]
