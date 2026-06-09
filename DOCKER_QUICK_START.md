# AttachmentLens Docker Quick Start

## ⚡ Fastest Way to Get Started

### On Windows:
1. **Double-click `rebuild-docker.bat`** in the project folder
2. Wait for the build to complete (1-2 minutes on first run)
3. Browser opens automatically to http://localhost:5000
4. Login with: `admin` / `admin`

That's it! ✓

---

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `rebuild-docker.bat` | **Full rebuild** - stops container, deletes old image, builds fresh, starts new container |
| `start-docker.bat` | Start the container (if already built) |
| `stop-docker.bat` | Stop the running container |
| `logs-docker.bat` | View live logs from the container |
| `open-browser.bat` | Open the app in your default browser |

---

## Command Line Usage

If you prefer the command line:

### First Time (with build):
```powershell
docker-compose up --build
```

### Subsequent Times (container already built):
```powershell
docker-compose up
```

### Stop:
```powershell
docker-compose down
```

### View Logs:
```powershell
docker-compose logs -f
```

---

## Prerequisites

- ✅ Docker Desktop installed
- ✅ Docker Desktop running

### Don't Have Docker?
1. Download: https://www.docker.com/products/docker-desktop
2. Install it
3. Launch Docker Desktop
4. Wait for it to show "Docker is running"
5. Then run `rebuild-docker.bat`

---

## Accessing the App

- **URL**: http://localhost:5000
- **Username**: `admin`
- **Password**: `admin`
- **Stats Page**: http://localhost:5000/stats

---

## What's Inside

The Docker container includes:
- Python 3.12
- Flask web framework
- Gunicorn WSGI server (production-grade)
- SQLite database
- All dependencies

Your database (`posts.db`) is automatically persisted between container restarts.

---

## Troubleshooting

### Docker Desktop not running?
1. Search for "Docker Desktop" in Windows Start menu
2. Click to launch
3. Wait 30-60 seconds for it to fully start
4. Then run the batch files

### Port 5000 already in use?
Edit `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Change first number to 5001
```
Then access at: http://localhost:5001

### Container won't start?
Run `logs-docker.bat` to see error messages

### Out of disk space?
```powershell
docker system prune -a
```

---

## Tips

- **Development**: Run the batch files, they handle everything
- **Logs**: Keep `logs-docker.bat` running in another window to see what's happening
- **Database**: Edit `posts.db` with any SQLite viewer
- **Performance**: If slow, give Docker more memory (Settings > Resources > Memory)

---

## Architecture

```
Your Laptop
    ↓
Docker Container (Isolated Environment)
    ├── Python 3.12
    ├── Gunicorn (WSGI Server)
    ├── Flask App
    ├── SQLite Database
    └── All Dependencies
    ↓
Browser Access: http://localhost:5000
```

---

## Next Steps

1. ✅ Start the container with `rebuild-docker.bat`
2. ✅ Open http://localhost:5000
3. ✅ Login with admin/admin
4. ✅ Check out the Stats page at /stats

Happy developing! 🚀
