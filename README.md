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