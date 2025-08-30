from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .routers import auth, projects, documents, analyses, reports
from .db import init_db

app = FastAPI(title="TCC Auditoria & Conformidade — API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    auth.seed_user()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
