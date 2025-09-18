# backend/app/services/analysis.py
import os, re
from typing import List, Dict, Any, Optional

# --------- Regras locais (PII Brasil + LGPD) ---------
CPF_RE   = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_RE  = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TEL_RE   = re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b")

KEYWORDS = {
    "lgpd_base_legal": ["base legal", "consentimento", "legítimo interesse", "contrato", "obrigação legal"],
    "lgpd_direitos": ["titular", "direito de acesso", "correção", "eliminação", "portabilidade"],
    "lgpd_governanca": ["dpo", "encarregado", "privacy by design", "privacy by default", "matriz de risco"],
    "lgpd_segurança": ["criptografia", "pseudonimização", "anonimização", "controle de acesso", "backup", "retenção", "retencao", "logs"],
    "revogacao_acesso": ["revogação de acesso", "desligamento", "offboarding", "acesso indevido", "segregação de funções", "sox"],
    "incidente": ["incidente de segurança", "vazamento", "notificação anpd", "breach"],
}

SEVERITY_WEIGHT = {
    "PII": 3,
    "revogacao_acesso": 3,
    "lgpd_segurança": 2,
    "lgpd_base_legal": 2,
    "lgpd_direitos": 2,
    "lgpd_governanca": 1,
    "incidente": 3,
}

def detect_pii(text: str) -> Dict[str, List[str]]:
    return {
        "cpf": CPF_RE.findall(text or ""),
        "cnpj": CNPJ_RE.findall(text or ""),
        "email": EMAIL_RE.findall(text or ""),
        "telefone": TEL_RE.findall(text or ""),
    }

def keyword_hits(text: str) -> Dict[str, List[str]]:
    t = (text or "").lower()
    hits = {}
    for bucket, words in KEYWORDS.items():
        found = [w for w in words if w in t]
        if found:
            hits[bucket] = found
    return hits

def severity_from_hits(hits: Dict[str, List[str]], pii: Dict[str, List[str]]) -> str:
    score = 0
    if any(pii.values()):
        score += SEVERITY_WEIGHT["PII"]
    for bucket in hits.keys():
        score += SEVERITY_WEIGHT.get(bucket, 1)
    return "alto" if score >= 5 else "médio" if score >= 3 else "baixo"

def summarize_local(text: str) -> str:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return "\n".join(lines[:3]) if lines else ""

# --------- LLM opcional (OpenAI) ---------
def _llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

def refine_with_llm(title: str, text: str, prelim: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not _llm_enabled():
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"""
Você é um auditor de conformidade LGPD. Com base no documento abaixo, valide e refine os achados.
Título: {title}

Trecho (pode estar truncado):
{text[:4000]}

Achados preliminares (JSON):
{prelim}

Responda em JSON com as chaves: resumo, achados, severidade, recomendacoes (máx 5).
"""
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        import json
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception:
        # Em caso de erro (timeout/limite/conexão), mantém o resultado local
        return None

def analyze_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    title = doc.get("title", f"doc-{doc.get('id')}")
    content = doc.get("content", "")
    pii = detect_pii(content)
    hits = keyword_hits(content)
    severity = severity_from_hits(hits, pii)
    prelim = {
        "resumo": summarize_local(content),
        "achados": {
            "pii": {k: v[:5] for k, v in pii.items() if v},
            "palavras_chave": hits,
        },
        "severidade": severity,
        "recomendacoes": [
            "Definir base legal e registrar evidências de consentimento quando aplicável.",
            "Endereçar processo de revogação de acessos no desligamento (offboarding).",
            "Estabelecer política de retenção e descarte de dados.",
            "Aplicar controles de segurança: criptografia, logs e segregação de funções.",
        ],
    }
    refined = refine_with_llm(title, content, prelim)
    return refined or prelim
