FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY services/compliance-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/compliance-engine /app/services/compliance-engine
COPY shared_schemas /app/shared_schemas

WORKDIR /app/services/compliance-engine

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]