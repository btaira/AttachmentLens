# Docker Setup for AttachmentLens

## Step 1: Start Docker Desktop

1. Open **Docker Desktop** application on your laptop (search for it in Windows)
2. Wait for it to fully load (you'll see the Docker icon in system tray)
3. It should say "Docker is running" when ready

## Step 2: Build the Docker Image

Open PowerShell or Command Prompt and run:

```powershell
cd C:\Users\btair\OneDrive\Documents\GitHub\AttachmentLens
docker build -t attachmentlens:latest .
```

Wait for the build to complete (5-10 minutes on first run).

## Step 3: Run the Container

### Option A: Using Docker Compose (Easier)

```powershell
docker-compose up
```

### Option B: Manual Docker Command

```powershell
docker run -p 5000:5000 -v "C:\Users\btair\OneDrive\Documents\GitHub\AttachmentLens\posts.db:/app/posts.db" attachmentlens:latest
```

## Step 4: Access the Application

Open your browser and go to:
- **http://localhost:5000**

Login with:
- Username: `admin`
- Password: `admin`

## Step 5: View Stats Page

Navigate to:
- **http://localhost:5000/stats**

You should see:
- ✓ All KPI metrics (Total Posts, Read, Unread, Favorites, etc.)
- ✓ Category breakdown chart
- ✓ Read vs Unread chart
- ✓ Timeline chart
- ✓ Top 10 posts

## Stopping the Container

Press `Ctrl+C` in the PowerShell window, or run:

```powershell
docker-compose down
```

## Why Docker?

Docker solves the Flask routing issue by using **Gunicorn**, a production-grade WSGI server. Flask's built-in development server has routing problems on your system, but Gunicorn handles all routes correctly.

## Troubleshooting

If port 5000 is already in use:

```powershell
# Change the port in docker-compose.yml
# Change "5000:5000" to "5001:5000" to use port 5001
docker-compose up
# Then access at http://localhost:5001
```

If Docker runs out of memory:
- Increase Docker's memory allocation in Docker Desktop settings
- Settings > Resources > Memory (set to at least 4GB)

## Database Persistence

The `posts.db` file is mounted as a volume, so your data persists between container restarts.

## View Logs

```powershell
docker-compose logs -f
```
