# Running AttachmentLens with Docker

Docker allows you to run AttachmentLens in a consistent environment. **Data persists across container sessions using volumes.**

## Quick Start

### Prerequisites
- Docker installed ([download](https://www.docker.com/products/docker-desktop))

### Run with Docker Compose (Easiest)

```bash
# Start the app
docker-compose up

# Visit http://localhost:5000
```

**Data is stored in `./data/posts.db` on your host machine.**

### Stop the app
```bash
docker-compose down
```

**Your database persists** — it's in the `./data/` folder locally.

---

## How Data Persistence Works

### The Problem
By default, Docker containers are **ephemeral** — when stopped, all files inside are deleted.

### The Solution: Volumes
Docker **volumes** mount a directory from your computer into the container:

```
Your Computer          Container
./data/ ←→ /app/data
```

When the container writes to `/app/data/posts.db`, it actually writes to `./data/posts.db` on your host machine.

This way:
- ✅ Data survives container restarts
- ✅ You can see files on your host machine
- ✅ Easy backups (just copy the `./data/` folder)

---

## Using Docker

### Build and Run Manually

```bash
# Build the image
docker build -t attachmentlens .

# Run with volume for persistence
docker run -p 5000:5000 -v $(pwd)/data:/app/data attachmentlens
```

**Windows PowerShell:**
```powershell
docker run -p 5000:5000 -v ${PWD}/data:/app/data attachmentlens
```

### Using Docker Compose (Recommended)

Just run:
```bash
docker-compose up
```

This does everything above automatically. See `docker-compose.yml`.

---

## Checking Your Data

### From Docker Compose
```bash
# List files in volume
docker-compose exec attachmentlens ls -la /app/data

# Or check locally
ls ./data
```

### From Manual Docker Run
```bash
# See what's in the volume
docker run -v $(pwd)/data:/app/data attachmentlens ls -la /app/data

# Or check locally
ls ./data
```

---

## Persistent Data Across Sessions

### Session 1: Import data
```bash
docker-compose up
# Visit http://localhost:5000
# Import posts, add highlights, etc.
docker-compose down
```

Database is saved to `./data/posts.db`

### Session 2: Data is there
```bash
docker-compose up
# Visit http://localhost:5000
# All your posts, highlights, and AI analyses are there!
docker-compose down
```

---

## Backing Up Your Database

### Backup locally
```bash
# Copy the data folder
cp -r data data-backup-$(date +%Y-%m-%d)
```

### Export to JSON
```bash
# Run export inside container
docker-compose exec attachmentlens python scripts/export_to_json.py /app/data/backup.json

# Or access from host
cat data/backup.json
```

---

## Environment Variables

You can customize behavior with environment variables:

### In `docker-compose.yml`:
```yaml
environment:
  - DB_PATH=/app/data/posts.db
  - FLASK_ENV=production
  - FLASK_DEBUG=0
```

### From command line:
```bash
docker run -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e DB_PATH=/app/data/posts.db \
  -e FLASK_ENV=production \
  attachmentlens
```

---

## Troubleshooting

### "Can't connect to the app"
- Make sure Docker is running
- Check port 5000 is available: `docker-compose ps`
- Wait 5 seconds for the app to start

### "Database is empty after restart"
- Check that volume is mounted: `docker-compose exec attachmentlens ls /app/data`
- Verify `./data/posts.db` exists on your host
- If missing, you may have run without volume — recreate it

### "Permission denied" on database file
```bash
# Fix file permissions
sudo chmod 666 data/posts.db  # macOS/Linux

# Windows: right-click → Properties → Security → Full Control
```

### "Port 5000 already in use"
```bash
# Use a different port in docker-compose.yml:
ports:
  - "8000:5000"  # Access at http://localhost:8000

# Or kill the process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

### Want to see app logs?
```bash
docker-compose logs -f attachmentlens
```

---

## Advanced: Multi-Container Setup with PostgreSQL

For production, use PostgreSQL instead of SQLite:

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: attachmentlens
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  attachmentlens:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://app:secure_password_here@db:5432/attachmentlens
    depends_on:
      - db
    volumes:
      - ./data:/app/data

volumes:
  postgres_data:
```

Then update `app.py` to use PostgreSQL:
```python
import os
from urllib.parse import quote_plus

db_url = os.getenv('DATABASE_URL')
if db_url:
    # Use PostgreSQL
    import psycopg2
    conn = psycopg2.connect(db_url)
else:
    # Fall back to SQLite
    conn = sqlite3.connect(os.getenv('DB_PATH', 'posts.db'))
```

---

## Deploying Docker to Production

### Option 1: Docker Hub
```bash
# Build image
docker build -t yourusername/attachmentlens .

# Push to Docker Hub
docker push yourusername/attachmentlens

# Deploy anywhere (Railway, DigitalOcean, AWS, etc.)
# They all support Docker images
```

### Option 2: Heroku (with Docker)
```bash
# Build
heroku container:push web

# Deploy
heroku container:release web

# View logs
heroku logs --tail
```

### Option 3: Railway (with Docker)
1. Upload `Dockerfile` to GitHub
2. Connect repo to Railway
3. Railway auto-detects Dockerfile
4. Deploy one-click

---

## Summary

| Aspect | SQLite (Local) | PostgreSQL (Production) |
|--------|---|---|
| **Setup** | docker-compose up | Multi-container compose |
| **Data Persistence** | Volume to host | PostgreSQL volume |
| **Scalability** | Single container | Scales easily |
| **Best For** | Personal use | Multi-user / production |
| **Backup** | Copy ./data folder | pg_dump command |

---

## Cheat Sheet

```bash
# Start
docker-compose up

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Access shell
docker-compose exec attachmentlens bash

# Run script in container
docker-compose exec attachmentlens python scripts/export_to_json.py /app/data/backup.json

# Check volume
docker-compose exec attachmentlens ls -la /app/data

# Rebuild image
docker-compose up --build
```

---

See [DEPLOYMENT.md](DEPLOYMENT.md) for other deployment options (Heroku, Railway, GitHub Pages, etc.).
