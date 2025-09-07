# KTL ISP Billing System - Docker Setup

This document provides instructions for running the KTL ISP Billing System using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd ktl_isp_billing
   ```

2. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Web Application: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/swagger/

4. **Default Admin Credentials**:
   - Username: `admin`
   - Password: `admin123`

## Services

The Docker Compose setup includes the following services:

### Web Application (`web`)
- Django application server
- Runs on port 8000
- Automatically handles database migrations
- Creates default superuser on first run

### Database (`db`)
- PostgreSQL 15
- Database name: `ktl_isp_db`
- Username: `postgres`
- Password: `postgres`
- Port: 5432

### Redis (`redis`)
- Redis 7 (Alpine)
- Used for caching and Celery message broker
- Port: 6379

### Celery Worker (`celery`)
- Background task processing
- Handles asynchronous tasks

### Celery Beat (`celery-beat`)
- Periodic task scheduler
- Handles scheduled tasks

## Environment Variables

The following environment variables are configured in docker-compose.yml:

```yaml
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-docker-development-key-change-in-production
DB_NAME=ktl_isp_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_URL=redis://redis:6379/1
```

## Common Commands

### Start services in background:
```bash
docker-compose up -d
```

### Stop services:
```bash
docker-compose down
```

### View logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs db
```

### Execute commands in containers:
```bash
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database operations:
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d ktl_isp_db

# Backup database
docker-compose exec db pg_dump -U postgres ktl_isp_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres ktl_isp_db < backup.sql
```

## Development Workflow

### Making code changes:
1. Code changes are automatically reflected (volume mounting)
2. For model changes, run migrations:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

### Installing new packages:
1. Add package to `requirements.in`
2. Rebuild the container:
   ```bash
   pip-compile requirements.in
   docker-compose build web
   docker-compose up -d
   ```

### Debugging:
```bash
# Access container shell
docker-compose exec web bash

# View Django logs
docker-compose logs -f web

# Check container status
docker-compose ps
```

## Production Considerations

For production deployment, consider:

1. **Security**:
   - Change default passwords
   - Use environment files for secrets
   - Enable HTTPS
   - Update `DJANGO_SECRET_KEY`

2. **Performance**:
   - Use production WSGI server (Gunicorn is included)
   - Configure proper database settings
   - Set up proper caching
   - Use external Redis/PostgreSQL services

3. **Monitoring**:
   - Add health checks
   - Set up logging aggregation
   - Monitor resource usage

## Troubleshooting

### Common Issues:

1. **Port conflicts**:
   ```bash
   # Change ports in docker-compose.yml if needed
   ports:
     - "8001:8000"  # Use different host port
   ```

2. **Database connection issues**:
   ```bash
   # Check if database is ready
   docker-compose logs db
   
   # Restart services
   docker-compose restart
   ```

3. **Permission issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

4. **Clean restart**:
   ```bash
   # Remove all containers and volumes
   docker-compose down -v
   docker-compose up --build
   ```

## API Testing

### Using curl:
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"login_id": "admin", "password": "admin123"}'

# Access protected endpoint
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Swagger UI:
Visit http://localhost:8000/swagger/ for interactive API documentation.

## Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Review this documentation
3. Check the main README.md for application-specific details
