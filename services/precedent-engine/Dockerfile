# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY shared_schemas /app/shared_schemas
# COPY . .
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
FROM python:3.11-slim
WORKDIR /app
COPY services/precedent-engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared_schemas /app/shared_schemas
COPY services/precedent-engine /app/services/precedent-engine
WORKDIR /app/services/precedent-engine
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]