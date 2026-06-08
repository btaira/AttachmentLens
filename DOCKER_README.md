# Running AttachmentLens in Docker

Docker runs the application with Gunicorn (a proper WSGI server) instead of Flask's development server. This solves routing issues and is suitable for production.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### Run with Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Access the app at http://localhost:5000
```

The database file (`posts.db`) will be persisted on your machine.

### Stop the container

```bash
docker-compose down
```

## Manual Docker Commands

If you prefer to run Docker manually:

```bash
# Build the image
docker build -t attachmentlens .

# Run the container
docker run -p 5000:5000 -v $(pwd)/posts.db:/app/posts.db attachmentlens
```

## Features

✓ Production-grade WSGI server (Gunicorn)
✓ Stats page fully functional
✓ All routes working properly
✓ Database persistence
✓ Easy to deploy

## Accessing the App

- Open your browser to: http://localhost:5000
- Login with default credentials: admin / admin
- Stats page at: http://localhost:5000/stats

## Logs

To see container logs:

```bash
docker-compose logs -f
```

Or with manual Docker:

```bash
docker logs -f <container_id>
```
