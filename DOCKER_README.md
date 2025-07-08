# Docker Setup for Shava Project

This document describes how to run the Shava project using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed (usually comes with Docker Desktop)

## Files Structure

```
├── backend/
│   ├── Dockerfile              # Development Dockerfile
│   ├── Dockerfile.prod         # Production Dockerfile
│   ├── .dockerignore          # Docker ignore file
│   └── ... (Django project files)
├── docker-compose.yml          # Development compose file
├── docker-compose.prod.yml     # Production compose file
├── nginx.conf                  # Nginx configuration
└── .env                       # Environment variables
```

## Environment Variables

Create a `.env` file in the root directory:

```env
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
POSTGRES_PASSWORD=your-secure-postgres-password
```

## Development Setup

### 1. Build and run the development environment:

```bash
docker-compose up --build
```

### 2. Access the application:

- Django app: http://localhost:8000
- PostgreSQL: localhost:5432

### 3. Run Django commands:

```bash
# Create migrations
docker-compose exec web poetry run python manage.py makemigrations

# Apply migrations
docker-compose exec web poetry run python manage.py migrate

# Create superuser
docker-compose exec web poetry run python manage.py createsuperuser

# Access Django shell
docker-compose exec web poetry run python manage.py shell
```

## Production Setup

### 1. Build and run the production environment:

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### 2. Access the application:

- Application: http://localhost (via Nginx)
- Direct Django: http://localhost:8000

## Useful Commands

### Stop all services:
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ This will delete your database):
```bash
docker-compose down -v
```

### View logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
```

### Execute commands in containers:
```bash
# Access Django shell
docker-compose exec web poetry run python manage.py shell

# Access PostgreSQL
docker-compose exec db psql -U shava_user -d shava_db
```

### Build only (without starting):
```bash
docker-compose build
```

### Rebuild without cache:
```bash
docker-compose build --no-cache
```

## Troubleshooting

### 1. Port already in use:
```bash
# Stop other services using port 8000
docker-compose down
# Or change the port in docker-compose.yml
```

### 2. Database connection issues:
```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db
```

### 3. Permission issues:
```bash
# Reset file permissions
sudo chown -R $USER:$USER .
```

### 4. Clear Docker cache:
```bash
docker system prune -a
```

## Security Notes

- Never commit your `.env` file
- Use strong passwords for production
- Consider using Docker secrets for production deployments
- Regularly update base images for security patches

## Performance Tips

- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds for production (already implemented)
- Use Docker BuildKit for faster builds
- Consider using Docker volumes for development hot-reloading
