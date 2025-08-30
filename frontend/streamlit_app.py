import os
import streamlit as st
import requests
from typing import Optional, Dict, Any

st.set_page_config(page_title="Auditoria & Conformidade — Streamlit", layout="wide")

# =============================
# Config & Session
# =============================
if "base_url" not in st.session_state:
    st.session_state.base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
if "token" not in st.session_state:
    st.session_state.token = None
if "projects" not in st.session_state:
    st.session_state.projects = []
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "docs" not in st.session_state:
    st.session_state.docs = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None


def api(path: str, method: str = "GET", json: Optional[dict] = None) -> Any:
    url = st.session_state.base_url.rstrip("/") + path
    headers = {"accept": "application/json"}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    if json is not None:
        headers["Content-Type"] = "application/json"
    resp = requests.request(method, url, json=json, headers=headers, timeout=30)
    if resp.status_code >= 400:
        st.error(f"Erro {resp.status_code}: {resp.text}")
        return None
    if resp.content:
        return resp.json()
    return None


# =============================
# Sidebar
# =============================
with st.sidebar:
    st.markdown("### Configuração")
    st.text_input("API Base URL", key="base_url", help="Ex.: http://localhost:8000")

    if st.session_state.token:
        st.success("Autenticado ✅")
        if st.button("Sair", use_container_width=True):
            st.session_state.token = None
            st.session_state.projects = []
            st.session_state.selected_project = None
            st.session_state.docs = []
            st.session_state.analysis = None
            st.rerun()
    else:
        st.info("Não autenticado")

st.title("Auditoria & Conformidade — Frontend (Streamlit)")

# =============================
# Login
# =============================
with st.expander("🔐 Login", expanded=st.session_state.token is None):
    username = st.text_input("Usuário", value="admin@local")
    password = st.text_input("Senha", value="admin", type="password")
    if st.button("Entrar", type="primary"):
        data = api("/auth/token", method="POST", json={"username": username, "password": password})
        if data and "access_token" in data:
            st.session_state.token = data["access_token"]
            st.success("Login realizado!")
            st.rerun()

if not st.session_state.token:
    st.stop()

# =============================
# Projetos
# =============================
st.header("📁 Projetos")
col1, col2 = st.columns([2,1])
with col1:
    with st.form("novo_projeto"):
        name = st.text_input("Nome do projeto", value="Piloto IA Compliance")
        description = st.text_input("Descrição", value="POC do TCC")
        if st.form_submit_button("Criar projeto"):
            p = api("/projects", method="POST", json={"name": name, "description": description})
            if p:
                st.success(f"Projeto criado: #{p['id']} {p['name']}")

with col2:
    if st.button("Carregar lista de projetos"):
        st.session_state.projects = api("/projects", method="GET") or []
    if st.session_state.projects:
        options = {f"#{p['id']} — {p['name']}": p["id"] for p in st.session_state.projects}
        sel = st.selectbox("Selecionar projeto", list(options.keys()))
        st.session_state.selected_project = options[sel]

if st.session_state.projects:
    st.dataframe(st.session_state.projects, use_container_width=True)

# =============================
# Documentos
# =============================
st.header("📄 Documentos")
if st.session_state.selected_project:
    with st.form("novo_doc"):
        title = st.text_input("Título", value="Política de IA")
        content = st.text_area("Conteúdo", value="Inclui transparência, governança, dados pessoais e segurança.")
        if st.form_submit_button("Adicionar documento"):
            d = api("/documents", method="POST", json={
                "project_id": st.session_state.selected_project,
                "title": title,
                "content": content
            })
            if d:
                st.success(f"Documento criado: #{d['id']} {d['title']}")
    if st.button("Carregar documentos"):
        st.session_state.docs = api(f"/documents/{st.session_state.selected_project}", method="GET") or []
    if st.session_state.docs:
        st.dataframe(st.session_state.docs, use_container_width=True)
else:
    st.info("Selecione um projeto.")

# =============================
# Análise
# =============================
st.header("🧠 Análise")
if st.session_state.selected_project:
    if st.button("Rodar análise"):
        st.session_state.analysis = api("/analyses/run", method="POST", json={"project_id": st.session_state.selected_project})
    if st.session_state.analysis:
        st.json(st.session_state.analysis)
else:
    st.info("Selecione um projeto.")
