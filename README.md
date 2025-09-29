# PyBins - Python Package Freezer


A Flask-based service for building and distributing Python packages as frozen binaries and installers.

## Features

- **Package Building**: Build Python packages into wheels or standalone binaries
- **Quick Install**: Get installer scripts for any PyPI package
- **Package Metadata**: Retrieve detailed information about packages
- **Build Management**: Track and manage package builds
- **RESTful API**: Complete REST API for all operations

## Quick Start

### Using Docker
```bash
docker-compose up --build
```

### Manual Setup
```bash
pip install -r requirements.txt
python -m pybins
```

## API Endpoints

### Core Endpoints
- `GET /` - API documentation and available endpoints
- `GET /health` - Service health check

### Package Operations
- `GET /<package>` - Get installer script for latest version
- `GET /<package>@<version>` - Get installer script for specific version
- `GET /meta/<package>` - Get package metadata from PyPI

### Build Management
- `POST /enqueue` - Enqueue a package build
- `POST /build` - Build a package immediately
- `GET /builds` - List all builds
- `GET /build/<build_id>` - Get specific build status

### Worker API
- `GET /worker/builds` - Worker-specific build listing
- `POST /worker/builds` - Create new build via worker
- `POST /worker/run` - Run immediate build via worker

### Storage Management
- `GET /packages` - List registered packages
- `POST /packages` - Register a new package

## Usage Examples

### Get an Installer Script
```bash
# Latest version
curl http://localhost:5000/requests

# Specific version
curl http://localhost:5000/requests@2.25.1
```

### Get Package Metadata
```bash
curl http://localhost:5000/meta/flask
```

### Build a Package
```bash
curl -X POST http://localhost:5000/build 
  -H "Content-Type: application/json" 
  -d '{"package": "requests", "version": "latest", "build_type": "wheel"}'
```

#### PowerShell (Windows)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/build" -Method POST -ContentType "application/json" -Body '{"package": "requests", "version": "latest", "build_type": "wheel"}'
```


### Build a Package (Binary)
```bash
curl -X POST http://localhost:5000/build \
  -H "Content-Type: application/json" \
  -d '{"package": "requests", "version": "latest", "build_type": "binary"}'
```

#### PowerShell (Windows)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/build" -Method POST -ContentType "application/json" -Body '{"package": "requests", "version": "latest", "build_type": "binary"}'
```

#### Binary Compatibility Notice

**Binaries built using the default Docker setup are Linux ELF executables, not Windows `.exe` files.**

- If you download a binary (e.g., `flask-binary.exe`) and see unreadable characters or `ELF` at the start when opening it, this means it is a Linux binary.
- You cannot run Linux binaries directly on Windows. To run the binary on Windows, you must build it in a Windows environment (or use a Windows-based Docker image).
- Only packages that provide a command-line entry point (CLI tools, not libraries) can be built as binaries.

**To build a Windows-compatible binary:**
1. Run the build process on a Windows machine (not in a Linux Docker container), or
2. Use a Windows-based Docker image for building (advanced).

If you need help with this, see the documentation or open an issue.

### Download Build Artifacts
After a successful build, the API response will include download URLs for the wheel, binary, or build log. You can download them using:

```bash
curl -O http://localhost:5000/download/<build_id>/<filename>
```

Or in PowerShell:
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/download/<build_id>/<filename>" -OutFile <filename>
```


### Enqueue a Build (Background Job)
The `/enqueue` endpoint now uses a background job queue (RQ/Redis) to process builds asynchronously. You must run an RQ worker for jobs to be processed.

```bash
curl -X POST http://localhost:5000/enqueue \
  -H "Content-Type: application/json" \
  -d '{"package": "flask", "version": "2.3.0"}'
```

#### PowerShell (Windows)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/enqueue" -Method POST -ContentType "application/json" -Body '{"package": "flask", "version": "2.3.0"}'
```

#### Running the Worker
You must have Redis running (default: `localhost:6379`). Then, in a separate terminal:

```bash
rq worker builds --path pybins
```

This will process enqueued build jobs in the background.

### Check Build Status
```bash
curl http://localhost:5000/build/<build_id>
```

## Architecture

```
pybins/
├── __init__.py         # Flask app factory
├── __main__.py         # Entry point for python -m pybins
├── api/
│   └── server.py       # API server blueprint
├── routes/
│   └── routes.py       # Main application routes
├── worker/
│   ├── urls.py         # Worker-specific routes
│   ├── tasks.py        # Build tasks and job management
│   └── models.py       # Data models
├── fetcher/
│   └── fetcher.py      # PyPI/GitHub package fetching
├── storage/
│   ├── models.py       # Storage data models
│   └── storage.py      # In-memory storage management
└── queue/
    └── setup.py        # Task queue configuration
```

## Configuration

The service can be configured via environment variables:

- `FLASK_ENV`: Set to 'development' or 'production'
- `FLASK_DEBUG`: Enable/disable debug mode
- `PORT`: Port to run the service on (default: 5000)

## Development

### Adding New Routes
1. Add routes to `routes/routes.py` using the `routes_bp` blueprint
2. For worker-specific routes, use `worker/urls.py` with `worker_bp` blueprint
3. For API routes, use `api/server.py` with `api_blueprint`

### Adding New Features
1. Implement core logic in appropriate modules (fetcher, storage, worker)
2. Add API endpoints in the relevant blueprint
3. Update this README with new endpoints

## License

This project is open source. Feel free to use, modify, and distribute.