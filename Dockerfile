FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /code

ENV PYTHONPATH=/code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]