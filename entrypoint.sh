#!/bin/bash

# Exit on any error
set -e

echo "=========================================="
echo "Starting KTL ISP Billing System..."
echo "=========================================="

# Function to check if a service is ready
wait_for_service() {
    local service=$1
    local host=$2
    local port=$3
    local timeout=${4:-30}

    echo "Waiting for $service to be ready at $host:$port..."
    local count=0
    while ! nc -z "$host" "$port"; do
        if [ $count -ge $timeout ]; then
            echo "ERROR: $service is not ready after $timeout seconds"
            exit 1
        fi
        count=$((count + 1))
        sleep 1
    done
    echo "$service is ready!"
}

# Wait for database to be ready
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    wait_for_service "database" "$DB_HOST" "$DB_PORT"
fi

# Wait for Redis to be ready (if Redis is configured)
if [ -n "$REDIS_URL" ]; then
    REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's|redis://\([^:]*\):\([^/]*\)/.*|\1|p')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's|redis://\([^:]*\):\([^/]*\)/.*|\2|p')
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        wait_for_service "Redis" "$REDIS_HOST" "$REDIS_PORT"
    fi
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell << EOF
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
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create necessary directories if they don't exist
mkdir -p /app/logs /app/media /app/staticfiles

# Set proper permissions
chmod -R 755 /app/staticfiles /app/media

echo "=========================================="
echo "Starting application server..."
echo "=========================================="

# Execute the command passed to the script
exec "$@"
