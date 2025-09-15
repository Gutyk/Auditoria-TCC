# Auditoria & Conformidade — Protótipo TCC

Protótipo funcional de alta fidelidade para auditoria de conformidade em sistemas corporativos com uso de Inteligência Artificial.  
Foco inicial: revogação de acessos e aderência à LGPD.
Link video mostrando projeto: https://www.youtube.com/watch?v=PMpv7b5ozpk

---

## Funcionalidades
- Login e autenticação via JWT.
- Criação e gerenciamento de projetos de auditoria.
- Upload e edição de documentos (texto e PDF parseado).
- Execução de análise de conformidade (MVP).
- Visualização de relatórios e evidências.
- Infraestrutura com Docker Compose (API, Frontend e PostgreSQL).

---

## Tecnologias
- *Backend*: Python 3.11, FastAPI, SQLAlchemy.  
- *Frontend*: Streamlit.  
- *Banco de Dados*: PostgreSQL 16.  
- *Infraestrutura*: Docker e Docker Compose.  
- *IA / NLP*: Estrutura planejada para embeddings e análise semântica.  
- *Autenticação*: JWT.  

---

## Como rodar com Docker
Pré-requisitos: Docker e Docker Compose instalados.

```bash
git clone https://github.com/seu-repo/auditoria-tcc.git
cd auditoria-tcc
docker compose up --build
```

<<<<<<< HEAD
caso não de build
``` bash
docker compose down -v
docker compose up --build
```

A API ficará em http://localhost:8000/docs
=======
Acessos locais:
>>>>>>> 9424789dc98a106cc14d69e519f24a237aa84d36

    API: http://localhost:8000/docs

Frontend: http://localhost:8501
Credenciais padrão

Usuário inicial para acesso ao sistema:

    Usuário: admin@local

    Senha: admin

Essas credenciais são criadas automaticamente ao iniciar o sistema e podem ser usadas para autenticar no frontend e gerar tokens no backend.
Cloud

O projeto foi desenvolvido para execução em ambiente local com Docker, mas está preparado para deploy em nuvem:

    Banco de Dados: o PostgreSQL pode ser substituído por serviços gerenciados como AWS RDS, GCP Cloud SQL ou Azure Database.

    API e Frontend: podem ser hospedados em ECS, AKS, GKE ou instâncias simples em EC2/VMs.

Justificativa: por se tratar de um MVP acadêmico, a execução local foi priorizada para simplificação e redução de custos. A utilização de contêineres garante portabilidade, possibilitando migração direta para provedores de nuvem quando necessário, sem alterações significativas na aplicação.
