FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY rules /app/rules
COPY playbooks /app/playbooks

ENV PYTHONPATH=/app/backend
ENV DATABASE_URL=sqlite:////app/data/soc_platform.db
RUN mkdir -p /app/data

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
