import os, io
from datetime import datetime
from typing import Optional, Any

import streamlit as st
import requests

# ---- parsers opcionais para upload ----
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None
try:
    import docx  # python-docx
except Exception:
    docx = None

st.set_page_config(page_title="Auditoria & Conformidade", layout="wide")
ss = st.session_state

# ---------------- estado ----------------
ss.base_url = ss.get("base_url", os.environ.get("API_BASE_URL", "http://localhost:8000"))
ss.token = ss.get("token")
ss.projects = ss.get("projects", [])
ss.selected_project = ss.get("selected_project")
ss.docs = ss.get("docs", [])
ss.selected_doc_id = ss.get("selected_doc_id")
ss.analysis = ss.get("analysis")
ss.doc_cache = ss.get("doc_cache", {})
ss.view = ss.get("view", "home")  # "home" | "project"

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
        st.error(f"Erro {r.status_code}: {r.text}")
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

def add_text_document(pid: int, title: str, content: str) -> bool:
    if not pid:
        st.error("Projeto não selecionado.")
        return False
    payload = {"project_id": int(pid), "title": title.strip(), "content": content}
    resp = api("/documents", "POST", json=payload)
    if resp:
        ss.doc_cache[resp.get("id", 0)] = content
        st.success("Documento criado")
        load_docs(pid)
        st.rerun()
        return True
    return False

def get_doc_detail(doc_id: int):
    return api(f"/documents/detail/{doc_id}", "GET")

def update_doc(doc_id: int, title: str, content: str):
    return api(f"/documents/{doc_id}", "PUT", json={"title": title, "content": content})

def delete_doc(doc_id: int):
    return api(f"/documents/{doc_id}", "DELETE")

def delete_project(pid: int):
    return api(f"/projects/{pid}", "DELETE")

def extract_text_from_upload(file) -> str:
    name = file.name.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        if not PdfReader:
            raise RuntimeError("Instale pypdf no frontend (requirements.txt).")
        reader = PdfReader(io.BytesIO(file.read()))
        parts = []
        for pg in reader.pages:
            try:
                parts.append(pg.extract_text() or "")
            except Exception:
                parts.append("")
        return "\n".join(parts)
    if name.endswith(".docx"):
        if not docx:
            raise RuntimeError("Instale python-docx no frontend (requirements.txt).")
        d = docx.Document(io.BytesIO(file.read()))
        return "\n".join(p.text for p in d.paragraphs)
    raise RuntimeError("Formato não suportado (PDF/DOCX/TXT)")

def fmt_created(value) -> str:
    if not value:
        return "—"
    # aceita datetime nativo ou ISO string
    if isinstance(value, str):
        try:
            if value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(value)
        except Exception:
            return value
    else:
        dt = value
    return dt.astimezone().strftime("%d/%m/%Y %H:%M")

# ------------- Sidebar -------------
with st.sidebar:
    st.markdown("## Auditoria & Conformidade")
    ss.base_url = st.text_input("API Base URL", value=ss.base_url)
    st.divider()
    if ss.token:
        if st.button("Sair", use_container_width=True):
            ss.clear()
            st.rerun()
        st.divider()

        if not ss.projects:
            load_projects()
        st.caption("Projetos")
        for p in ss.projects:
            if st.button(p["name"], key=f"side_{p['id']}", use_container_width=True):
                open_project(p["id"])
    else:
        with st.form("login"):
            u = st.text_input("Usuário", value="admin@local")
            p = st.text_input("Senha", value="admin", type="password")
            if st.form_submit_button("Entrar"):
                data = api("/auth/token", "POST", json={"username": u, "password": p})
                if data and "access_token" in data:
                    ss.token = data["access_token"]
                    load_projects()
                    st.success("Login realizado")
                    st.rerun()

if not ss.token:
    st.stop()

# ------------- Header / Nav -------------
colA, colB, colC = st.columns([1,6,2], vertical_alignment="center")
with colA:
    if st.button("Home", use_container_width=True, disabled=(ss.view == "home")):
        ss.view = "home"; ss.selected_project = None; ss.selected_doc_id = None; st.rerun()
with colB:
    st.markdown("### " + ("Projects" if ss.view == "home" else "Project"))
with colC:
    pass

st.write("")

# ------------- HOME -------------
if ss.view == "home":
    if not ss.projects:
        load_projects()

    # Criar novo projeto
    c1, c2 = st.columns([5,2])
    with c2:
        with st.popover("Novo projeto", use_container_width=True):
            with st.form("new_project"):
                name = st.text_input("Nome", value="Novo Projeto")
                desc = st.text_input("Descrição", value="MVP de auditoria e conformidade")
                submit = st.form_submit_button("Criar")
                if submit:
                    p = api("/projects", "POST", json={"name": name, "description": desc})
                    if p:
                        st.success("Projeto criado")
                        load_projects()
                        st.rerun()

    # Grid de cards
    if ss.projects:
        cols = st.columns(4)
        for i, p in enumerate(ss.projects):
            with cols[i % 4]:
                with st.container(border=True):
                    st.caption("PROJECT NAME")
                    st.markdown(f"**{p['name']}**")
                    st.caption(p.get("description") or "—")
                    b1, b2 = st.columns([1,1])
                    if b1.button("Abrir", key=f"open_{p['id']}", use_container_width=True):
                        open_project(p["id"])
                    # exclusão com confirmação simples
                    if b2.button("Excluir", key=f"del_proj_{p['id']}", use_container_width=True):
                        ss.to_delete_proj = p["id"]
                        st.rerun()
                if ss.get("to_delete_proj") == p["id"]:
                    with st.container(border=True):
                        st.warning(f"Confirmar exclusão do projeto #{p['id']}? Esta ação é irreversível.")
                        cdel1, cdel2 = st.columns([1,1])
                        if cdel1.button("Confirmar", key=f"confirm_proj_{p['id']}"):
                            resp = delete_project(p["id"])
                            ss.to_delete_proj = None
                            if resp is not None:
                                st.success("Projeto excluído")
                                ss.selected_project = None
                                load_projects()
                                st.rerun()
                        if cdel2.button("Cancelar", key=f"cancel_proj_{p['id']}"):
                            ss.to_delete_proj = None
                            st.rerun()
    else:
        st.info("Nenhum projeto. Crie um com 'Novo projeto'.")

# ------------- PROJETO -------------
else:
    if not ss.selected_project:
        st.info("Selecione um projeto.")
        st.stop()

    proj = next((p for p in ss.projects if p["id"] == ss.selected_project), None)
    st.caption(proj["name"] if proj else f"Projeto #{ss.selected_project}")

    left, right = st.columns([1.2, 3], gap="large")

    # -------- esquerda: lista de documentos + criar/upload
    with left:
        search = st.text_input("Buscar documento por título", key="doc_search", placeholder="Digite para filtrar")
        if not ss.docs:
            load_docs(ss.selected_project)
        docs = ss.docs
        if search and search.strip():
            docs = [d for d in docs if search.lower() in d["title"].lower()]

        st.markdown("#### Documentos")
        if not docs:
            st.info("Nenhum documento neste projeto.")
        else:
            for d in docs:
                created = fmt_created(d.get("created_at"))
                line = f"{d['title']}  \nCriado em: {created}"
                row = st.columns([6,1,1])
                with row[0]:
                    if st.button(line, key=f"doc_{d['id']}", use_container_width=True):
                        ss.selected_doc_id = d["id"]
                        st.rerun()
                with row[1]:
                    if st.button("Abrir", key=f"openbtn_{d['id']}", use_container_width=True):
                        ss.selected_doc_id = d["id"]
                        st.rerun()
                with row[2]:
                    if st.button("Excluir", key=f"deldoc_{d['id']}", use_container_width=True):
                        ss.to_delete_doc = d["id"]
                        st.rerun()

                if ss.get("to_delete_doc") == d["id"]:
                    with st.container(border=True):
                        st.warning(f"Confirmar exclusão do documento #{d['id']}?")
                        c1, c2 = st.columns([1,1])
                        if c1.button("Confirmar", key=f"confirm_doc_{d['id']}"):
                            resp = delete_doc(d["id"])
                            ss.to_delete_doc = None
                            if resp is not None:
                                st.success("Documento excluído")
                                if ss.selected_doc_id == d["id"]:
                                    ss.selected_doc_id = None
                                load_docs(ss.selected_project)
                                st.rerun()
                        if c2.button("Cancelar", key=f"cancel_doc_{d['id']}"):
                            ss.to_delete_doc = None
                            st.rerun()

        st.divider()
        with st.expander("Novo documento (texto)", expanded=False):
            with st.form("form_new_text_doc"):
                t_title = st.text_input("Título", value="Novo documento")
                t_content = st.text_area("Conteúdo", height=140)
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    if not t_title.strip():
                        st.warning("Informe um título.")
                    elif not t_content.strip():
                        st.warning("Informe o conteúdo.")
                    else:
                        add_text_document(ss.selected_project, t_title, t_content)

        with st.expander("Upload (PDF/DOCX/TXT)", expanded=False):
            up = st.file_uploader("Arquivo", type=["pdf", "docx", "txt"], key="up_inline")
            up_title = st.text_input("Título do arquivo", value=(up.name if up else "Arquivo importado"), key="up_title_inline")
            if st.button("Salvar do arquivo", disabled=up is None, key="btn_save_from_file_inline"):
                try:
                    text = extract_text_from_upload(up)
                except Exception as e:
                    st.error(str(e))
                else:
                    add_text_document(ss.selected_project, up_title, text)

        st.divider()
        # excluir projeto a partir da tela do projeto
        with st.expander("Excluir projeto", expanded=False):
            st.warning("Esta ação remove o projeto e todos os documentos associados (se o backend estiver configurado para cascade).")
            c1, c2 = st.columns([1,1])
            if c1.button("Confirmar exclusão do projeto", key="confirm_del_project"):
                resp = delete_project(ss.selected_project)
                if resp is not None:
                    st.success("Projeto excluído")
                    ss.selected_project = None
                    ss.view = "home"
                    load_projects()
                    st.rerun()
            if c2.button("Cancelar", key="cancel_del_project"):
                st.info("Exclusão cancelada.")

    # -------- direita: editor do documento selecionado
    with right:
        st.markdown("#### Editor")
        if not ss.selected_doc_id:
            st.info("Selecione um documento para visualizar/editar.")
        else:
            detail = get_doc_detail(ss.selected_doc_id)
            if not detail:
                st.error("Não foi possível carregar o documento.")
            else:
                colA, colB = st.columns([3,1])
                with colA:
                    new_title = st.text_input("Título", value=detail["title"], key=f"title_{detail['id']}")
                with colB:
                    created_display = fmt_created(detail.get("created_at"))
                    st.text_input("Criado em", value=created_display, disabled=True, key=f"created_{detail['id']}")
                new_content = st.text_area("Conteúdo", value=detail["content"], height=320, key=f"content_{detail['id']}")

                c1, c2, c3 = st.columns([1,1,6])
                if c1.button("Salvar", key=f"save_{detail['id']}"):
                    updated = update_doc(detail["id"], new_title, new_content)
                    if updated:
                        st.success("Documento atualizado")
                        load_docs(ss.selected_project)
                        st.rerun()
                if c2.button("Fechar", key="close_editor"):
                    ss.selected_doc_id = None
                    st.rerun()
