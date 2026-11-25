# Auditoria e Conformidade com IA

Protótipo desenvolvido como Trabalho de Conclusão de Curso em Sistemas de Informação na FIAP. O projeto explora como a análise de documentos pode apoiar auditorias internas, com foco em revogação de acessos e conformidade com a LGPD.

- [Leia o TCC completo em PDF](docs/auditoria-e-conformidade-tcc.pdf)
- [Assista à demonstração do protótipo](https://www.youtube.com/watch?v=PMpv7b5ozpk)

## O que o protótipo faz

1. Cria projetos de auditoria e reúne os documentos de cada projeto.
2. Importa arquivos PDF com texto selecionável, DOCX e TXT, ou recebe texto digitado. O conteúdo importado pode ser revisado antes da análise.
3. Analisa um documento por vez ou todos os documentos de um projeto. O modo local usa regras e palavras-chave para sinalizar possíveis dados pessoais e temas de conformidade.
4. Exibe um resumo e uma classificação preliminar de risco por documento. Quando configurada, a integração com a OpenAI pode complementar a análise local.

Os resultados servem como apoio à revisão humana. Use documentos fictícios na demonstração, especialmente com a integração externa habilitada, pois ela envia conteúdo dos documentos ao provedor.

## Arquitetura

| Camada | Tecnologias e responsabilidade |
| --- | --- |
| Interface | Streamlit para gerenciar projetos, revisar documentos e visualizar resultados |
| API | Python 3.11 e FastAPI, com login de demonstração via JWT |
| Persistência | SQLAlchemy e PostgreSQL 16 |
| Execução local | Docker Compose para subir a interface, a API e o banco |

- [`app/routers/`](app/routers/) reúne as rotas de autenticação, projetos, documentos, análises e relatórios.
- [`app/services/analyses.py`](app/services/analyses.py) implementa a análise local e a integração opcional com o modelo de linguagem.
- [`frontend/streamlit_app.py`](frontend/streamlit_app.py) contém a interface do protótipo.

## Como executar localmente

Instale o Git e o Docker com Compose. No terminal, clone e abra o repositório.

```bash
git clone https://github.com/Gutyk/Auditoria-TCC.git
cd Auditoria-TCC
```

Crie um arquivo `.env` na raiz com a configuração do banco local e uma chave JWT própria. Você pode gerar a chave com `openssl rand -hex 32`.

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/tcc_auditoria
SECRET_KEY=substitua_pela_sua_chave_gerada
```

Para testar o refinamento com IA, adicione `OPENAI_API_KEY` ao `.env`. `OPENAI_MODEL` é opcional. Sem a chave de API, a análise local continua disponível.

```bash
docker compose up --build
```

| Acesso | Endereço |
| --- | --- |
| Interface Streamlit | [localhost:8501](http://localhost:8501) |
| Documentação interativa da API | [localhost:8000/docs](http://localhost:8000/docs) |

Entre na interface com `admin@local` e senha `admin`, criados para a demonstração local. Crie um projeto, adicione um documento fictício e execute a análise.

Para acompanhar a inicialização, use `docker compose logs -f db api`. Para encerrar os serviços preservando os dados do banco local, use `docker compose down`.
