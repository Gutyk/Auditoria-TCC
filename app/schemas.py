# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------- Auth ----------
class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Projects ----------
class ProjectIn(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True  

# ---------- Documents ----------
class DocumentIn(BaseModel):
    project_id: int
    title: str
    content: str

class DocumentOut(BaseModel):
    id: int
    project_id: int
    title: str
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True

# Detalhe (inclui conteúdo)
class DocumentDetailOut(DocumentOut):
    content: str

# Atualização parcial
class DocumentUpdateIn(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# ---------- Analyses ----------
class AnalysisRunIn(BaseModel):
    project_id: int
    document_ids: Optional[List[int]] = None

class AnalysisDocResult(BaseModel):
    document_id: int
    title: str
    created_at: Optional[datetime] = None
    result: Dict[str, Any]

