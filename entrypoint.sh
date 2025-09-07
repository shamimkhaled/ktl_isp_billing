#!/bin/bash

# Exit on any error
set -e

echo "Starting KTL ISP Billing System..."

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(login_id='admin').exists():
    User.objects.create_superuser(
        login_id='shamimkhaled',
        email='shamimkhaled@ktl.com',
        password='admin9999',
        name='System Administrator'
    )
    print('Superuser created: shamimkhaled/admin9999')
else:
    print('Superuser already exists')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting Django development server..."
exec "$@"
