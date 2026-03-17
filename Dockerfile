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

# Run migrations then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
