import os, io
import streamlit as st
import requests
from typing import Optional, Any

# -------- parsers opcionais para upload --------
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None
try:
    import docx 
except Exception:
    docx = None

st.set_page_config(page_title="MTD TOOLS — Auditoria & Conformidade", layout="wide")
ss = st.session_state

# ------------- estado -------------
ss.base_url = ss.get("base_url", os.environ.get("API_BASE_URL", "http://localhost:8000"))
ss.token = ss.get("token")
ss.projects = ss.get("projects", [])
ss.selected_project = ss.get("selected_project")
ss.docs = ss.get("docs", [])
ss.analysis = ss.get("analysis")
ss.doc_cache = ss.get("doc_cache", {})
ss.view = ss.get("view", "home")  # "home" ou "project"
ss.selected_doc_id = ss.get("selected_doc_id")

# ------------- helpers de API -------------
def api(path: str, method: str = "GET", json: Optional[dict] = None, files=None, data=None) -> Any:
    url = ss.base_url.rstrip("/") + path
    headers = {"accept": "application/json"}
    if ss.token:
        headers["Authorization"] = f"Bearer {ss.token}"
    if json is not None:
        headers["Content-Type"] = "application/json"
    r = requests.request(method, url, json=json, files=files, data=data, headers=headers, timeout=60)
    if r.status_code >= 400:
        st.toast(f"Erro {r.status_code}", icon="❌")
        try:
            st.error(r.text)
        except Exception:
            pass
        return None
    return r.json() if r.content else None

def load_projects():
    ss.projects = api("/projects", "GET") or []

def load_docs(pid: int):
    ss.docs = api(f"/documents/{pid}", "GET") or []

def open_project(pid: int):
    ss.selected_project = pid
    ss.view = "project"
    ss.selected_doc_id = None
    load_docs(pid)
    st.rerun()

def add_text_document(pid: int, title: str, content: str):
    d = api("/documents", "POST", {"project_id": pid, "title": title, "content": content})
    if d:
        ss.doc_cache[d["id"]] = content
        st.toast("Documento criado", icon="✅")
        load_docs(pid)
        st.rerun()

def extract_text_from_upload(file) -> str:
    name = file.name.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        if not PdfReader:
            raise RuntimeError("Instale pypdf no frontend")
        reader = PdfReader(io.BytesIO(file.read()))
        texts = []
        for pg in reader.pages:
            try:
                texts.append(pg.extract_text() or "")
            except Exception:
                texts.append("")
        return "\n".join(texts)
    if name.endswith(".docx"):
        if not docx:
            raise RuntimeError("Instale python-docx no frontend")
        d = docx.Document(io.BytesIO(file.read()))
        return "\n".join(p.text for p in d.paragraphs)
    raise RuntimeError("Formato não suportado (PDF/DOCX/TXT)")

def run_analysis(pid: int):
    a = api("/analyses/run", "POST", {"project_id": pid})
    if a:
        ss.analysis = a
        st.toast("Análise concluída", icon="🧠")
        st.rerun()

# rotas novas do backend (recomendadas)
def get_doc_detail(doc_id: int):
    return api(f"/documents/detail/{doc_id}", "GET")

def update_doc(doc_id: int, title: str, content: str):
    return api(f"/documents/{doc_id}", "PUT", {"title": title, "content": content})

# ------------- Sidebar (login + lista) -------------
with st.sidebar:
    st.markdown("## MTD TOOLS")
    ss.base_url = st.text_input("API Base URL", value=ss.base_url)
    st.divider()
    if ss.token:
        if st.button("Sair", use_container_width=True):
            ss.clear(); st.rerun()
        st.divider()
        if not ss.projects:
            load_projects()
        st.caption("Projetos")
        for p in ss.projects:
            if st.button(f"🏷 {p['name']}", key=f"side_{p['id']}", use_container_width=True):
                open_project(p["id"])
    else:
        with st.form("login"):
            u = st.text_input("Usuário", value="admin@local")
            p = st.text_input("Senha", value="admin", type="password")
            if st.form_submit_button("Entrar"):
                data = api("/auth/token", "POST", {"username": u, "password": p})
                if data and "access_token" in data:
                    ss.token = data["access_token"]
                    load_projects()
                    st.toast("Login ok", icon="✅")
                    st.rerun()

if not ss.token:
    st.stop()

# ------------- Header -------------
left_h, mid_h, right_h = st.columns([1,6,1])
with left_h:
    if st.button("🏠 Home", use_container_width=True, disabled=(ss.view=="home")):
        ss.view = "home"; ss.selected_doc_id = None; st.rerun()
with mid_h:
    st.markdown("### " + ("PROJECTS" if ss.view=="home" else "PROJECT"))
with right_h:
    pass

st.write("")

# ------------- VIEW: HOME -------------
if ss.view == "home":
    if not ss.projects:
        load_projects()

    # criar novo projeto
    c1, c2 = st.columns([5,1])
    with c2:
        with st.popover("➕ Novo projeto", use_container_width=True):
            with st.form("new_project"):
                name = st.text_input("Nome", value="Novo Projeto")
                desc = st.text_input("Descrição", value="Guided risk assessment • IT elements")
                if st.form_submit_button("Criar"):
                    p = api("/projects", "POST", {"name": name, "description": desc})
                    if p:
                        load_projects()
                        st.rerun()

    if ss.projects:
        cols = st.columns(4)
        for i, p in enumerate(ss.projects):
            with cols[i % 4]:
                with st.container(border=True):
                    st.caption("PROJECT NAME")
                    st.markdown(f"**{p['name']}**")
                    st.caption(p.get("description") or "—")
                    b1, b2 = st.columns(2)
                    if b1.button("Abrir", key=f"open_{p['id']}", use_container_width=True):
                        open_project(p["id"])
                    b2.button("⋮", key=f"menu_{p['id']}", use_container_width=True, disabled=True)
    else:
        st.info("Sem projetos. Crie um com ➕.")

# ------------- VIEW: PROJETO -------------
else:
    if not ss.selected_project:
        st.info("Selecione um projeto."); st.stop()

    proj = next((p for p in ss.projects if p["id"] == ss.selected_project), None)
    st.caption(proj["name"] if proj else f"Projeto #{ss.selected_project}")
    st.caption("GUIDED RISK ASSESSMENT • IT ELEMENTS")

    # layout: esquerda (lista) / direita (editor)
    left, right = st.columns([1.2, 3], gap="large")

    # ===== esquerda: lista de documentos =====
    with left:
        q = st.text_input("Search…", key="doc_search", placeholder="Buscar por título")
        if not ss.docs:
            load_docs(ss.selected_project)

        docs = ss.docs
        if q and q.strip():
            docs = [d for d in docs if q.lower() in d["title"].lower()]

        st.markdown("#### Documentos")
        if not docs:
            st.info("Nenhum documento. Crie abaixo.")
        else:
            for d in docs:
                created = d.get("created_at") or "—"
                label = f"📄 {d['title']}  \n🕒 {created}"
                if st.button(label, key=f"doc_{d['id']}", use_container_width=True):
                    ss.selected_doc_id = d["id"]
                    st.rerun()

        st.divider()
        with st.expander("➕ Novo documento (texto)", expanded=False):
            with st.form("new_text_doc_inline"):
                t_title = st.text_input("Título", value="Novo documento")
                t_content = st.text_area("Conteúdo", height=140)
                if st.form_submit_button("Salvar"):
                    add_text_document(ss.selected_project, t_title, t_content)

        with st.expander("📎 Upload (PDF/DOCX/TXT)", expanded=False):
            up = st.file_uploader("Arquivo", type=["pdf","docx","txt"], key="up_inline")
            up_title = st.text_input("Título do arquivo", value=(up.name if up else "Arquivo importado"), key="up_title_inline")
            if st.button("Salvar do arquivo", disabled=up is None, key="btn_save_from_file_inline"):
                try:
                    text = extract_text_from_upload(up)
                except Exception as e:
                    st.error(str(e))
                else:
                    add_text_document(ss.selected_project, up_title, text)

    # ===== direita: editor =====
    with right:
        st.markdown("#### Editor")
        if not ss.selected_doc_id:
            st.info("Clique em um documento à esquerda para visualizar/editar.")
        else:
            detail = get_doc_detail(ss.selected_doc_id)
            if not detail:
                st.error("Não foi possível carregar o documento.")
            else:
                colA, colB = st.columns([3,1])
                with colA:
                    new_title = st.text_input("Título", value=detail["title"], key=f"title_{detail['id']}")
                with colB:
                    st.text_input("Criado em", value=(detail.get("created_at") or "—"), disabled=True, key=f"created_{detail['id']}")

                new_content = st.text_area("Conteúdo", value=detail["content"], height=300, key=f"content_{detail['id']}")

                c1, c2, c3 = st.columns([1,1,6])
                if c1.button("💾 Salvar", type="primary", key=f"save_{detail['id']}"):
                    updated = update_doc(detail["id"], new_title, new_content)
                    if updated:
                        st.toast("Documento atualizado", icon="✅")
                        load_docs(ss.selected_project)  # reflete mudanças na lista
                        st.rerun()
                if c2.button("↩ Voltar", key="back_list"):
                    ss.selected_doc_id = None
                    st.rerun()
