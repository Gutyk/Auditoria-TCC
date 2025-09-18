
# Stub de "analisador" para MVP. Substituir por pipeline real:
# - Normalização do texto (tokenização/lemmatização)
# - Extração de requisitos (regulatórios) -> base vetorial
# - Similaridade / regras heurísticas
# - Geração de sumário com evidências

from typing import Iterable
from dataclasses import dataclass

@dataclass
class Finding:
    requirement: str
    status: str  # e.g., "OK", "GAP", "PARTIAL"
    evidence: str

def run_analysis(texts: Iterable[str]) -> str:
    # Exemplo bobo: marca como "GAP" se não encontrar palavras-chave
    required = ["transparência", "governança", "dados pessoais", "rastreamento", "segurança"]
    all_text = "\n".join(texts).lower()

    findings = []
    for req in required:
        if req in all_text:
            findings.append(Finding(req, "OK", f"Termo encontrado: '{req}'"))
        else:
            findings.append(Finding(req, "GAP", f"Ausência do termo: '{req}'"))

    # Gera resumo textual
    ok = sum(1 for f in findings if f.status == "OK")
    gap = sum(1 for f in findings if f.status == "GAP")
    summary_lines = [
        f"Requisitos verificados: {len(required)}",
        f"Atendidos (OK): {ok}",
        f"Não atendidos (GAP): {gap}",
        "",
        "Detalhes:",
    ]
    for f in findings:
        summary_lines.append(f"- {f.requirement}: {f.status} — {f.evidence}")
    return "\n".join(summary_lines)
