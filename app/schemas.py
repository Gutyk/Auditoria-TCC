from pydantic import BaseModel, Field
from typing import Optional, List

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProjectIn(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class DocumentIn(BaseModel):
    project_id: int
    title: str
    content: str

class DocumentOut(BaseModel):
    id: int
    project_id: int
    title: str

    class Config:
        from_attributes = True

class AnalysisRunIn(BaseModel):
    project_id: int
    document_ids: Optional[List[int]] = None

class AnalysisOut(BaseModel):
    id: int
    project_id: int
    status: str
    summary: str

    class Config:
        from_attributes = True
