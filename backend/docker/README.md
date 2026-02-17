# 🐳 ScholarForm AI - Docker Infrastructure

This directory contains the Docker configuration for the ScholarForm AI platform.

## 📂 Structure
- `docker-compose.yml`: Defines the multi-container application (Backend, Frontend, Redis, Grobid, Celery).
- `Dockerfile.backend`: Build instructions for the Python FastAPI application.
- `Dockerfile.frontend`: Build instructions for the React application.
- `prometheus/`: Configuration for Prometheus monitoring.
- `grafana/`: Dashboards for Grafana.

## 🚀 Quick Start

1. **Navigate to this directory:**
   ```bash
   cd backend/docker
   ```

2. **Start the stack:**
   ```bash
   docker-compose up --build
   ```

3. **Access Services:**
   - **Frontend:** `http://localhost:5173`
   - **Backend API:** `http://localhost:8000`
   - **Grobid:** `http://localhost:8070`
   - **Prometheus:** `http://localhost:9090`
   - **Grafana:** `http://localhost:3000` (Default creds: admin/admin)

## ⚙️ Configuration

Environment variables are defined in the `docker-compose.yml` file or can be provided via a `.env` file in this directory.

**Key Variables:**
- `GROBID_SERVER_URL`: URL for the Grobid service (default: `http://grobid:8070`).
- `REDIS_URL`: URL for Redis (default: `redis://redis:6379/0`).
- `CELERY_BROKER_URL`: Broker for background tasks.
- `CORS_ORIGINS`: Allowed frontend origins.

## 🧹 Maintenance

- **Clean up volumes (Reset DB/Cache):**
  ```bash
  docker-compose down -v
  ```

- **View Logs:**
  ```bash
  docker-compose logs -f backend
  ```
