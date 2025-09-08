#!/bin/bash

# Exit on any error
set -e

echo "=========================================="
echo "Starting KTL ISP Billing System..."
echo "Environment: ${DJANGO_SETTINGS_MODULE:-config.settings.development}"
echo "Debug mode: ${DJANGO_DEBUG:-True}"
echo "=========================================="

# Function to check if a service is ready
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local timeout=${4:-30}

    echo "Waiting for $service to be ready at $host:$port..."
    local count=0
    while ! nc -z "$host" "$port" 2>/dev/null; do
        if [ $count -ge $timeout ]; then
            echo "WARNING: $service is not ready after $timeout seconds, continuing anyway..."
            return 0
        fi
        count=$((count + 1))
        sleep 1
    done
    echo "$service is ready!"
}

# Wait for database to be ready (if configured)
if [ -n "${DB_HOST:-}" ] && [ -n "${DB_PORT:-}" ]; then
    wait_for_service "database" "$DB_HOST" "$DB_PORT" 60
fi

# Wait for Redis to be ready (if Redis is configured)
if [ -n "${REDIS_URL:-}" ]; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's|redis://\([^:]*\):\([^/]*\)/.*|\1|p')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's|redis://\([^:]*\):\([^/]*\)/.*|\2|p')
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        wait_for_service "Redis" "$REDIS_HOST" "$REDIS_PORT" 30
    fi
fi

# Check if Django can start (basic check)
echo "Testing Django configuration..."
python manage.py check --deploy || {
    echo "WARNING: Django check failed, but continuing..."
}

# Run database migrations with error handling
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "ERROR: Database migrations failed"
    echo "This might be expected on first deployment or if database is not available"
    echo "Continuing with application startup..."
}

# Create superuser if it doesn't exist (with error handling)
echo "Checking for superuser..."
python manage.py shell << 'EOF' || echo "Could not create superuser, continuing..."
import sys
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(user_type='super_admin').exists():
        User.objects.create_superuser(
            login_id='shamimkhaled',
            email='shamimkhaled@ktl.com',
            password='admin9999',
            name='System Administrator',
            user_type='super_admin'
        )
        print('Superuser created: shamimkhaled/admin9999')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Error creating superuser: {e}')
    sys.exit(0)  # Exit successfully to continue with startup
EOF

# Collect static files (with error handling)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    echo "WARNING: Static files collection failed, continuing..."
}

# Create necessary directories if they don't exist
mkdir -p /app/logs /app/media /app/staticfiles

# Set proper permissions (only if we have write access)
chmod -R 755 /app/staticfiles /app/media 2>/dev/null || echo "Could not set permissions, continuing..."

echo "=========================================="
echo "Configuration complete. Starting application server..."
echo "Command: $@"
echo "=========================================="

# Execute the command passed to the script
exec "$@"