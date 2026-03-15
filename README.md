# Prerequisites
Before running the project, ensure the following software is installed on your system:

Docker
Docker Compose

Verify installation:

docker --version
docker compose version

If Docker is not installed:
https://docs.docker.com/get-docker/

# Running the Application

Build and start the containers:
    docker compose up --build

This will start:
    PostgreSQL database
    FastAPI application

# Database Migrations

This project uses Alembic for schema migrations.

Apply all pending migrations:
    make migrate

Create a new migration after changing models:
    make migrate-create msg="describe your change"