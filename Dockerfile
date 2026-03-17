FROM python:3.12-slim

WORKDIR /code

# Install dependencies first (layer cache)
COPY backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /code

ENV PYTHONPATH=/code
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run migrations then start the server.
# If DATABASE_URL is not explicitly set, construct it from POSTGRES_* vars
# (useful when running via docker-compose without a .env file).
CMD ["sh", "-c", "export DATABASE_URL=${DATABASE_URL:-postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}} && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
