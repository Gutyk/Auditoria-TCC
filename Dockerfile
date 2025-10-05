FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Só instale build-essential se alguma lib nativa exigir; senão, pode remover.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# Usuário sem privilégios
RUN useradd -m appuser

WORKDIR /app

# Dependências primeiro (melhor cache)
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Código por último
COPY app ./app

# Permissões para o usuário
RUN chown -R appuser:appuser /app

EXPOSE 8000
USER appuser

# Produção: sem --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
