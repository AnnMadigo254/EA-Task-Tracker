#!/bin/bash

# Wait for database to be ready
echo "⏳ Waiting for MariaDB to be ready..."
while ! nc -z db 3306; do
  sleep 1
done
echo "✅ MariaDB is ready!"

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Check if data already exists
TASK_COUNT=$(python manage.py shell -c "from tasks.models import Task; print(Task.objects.count())")

if [ "$TASK_COUNT" -eq "0" ]; then
    echo "📊 No tasks found. Importing EA tasks..."
    
    # Check if Excel file exists
    if [ -f "/app/EA_Tasks.xlsx" ]; then
        python import_ea_tasks.py
        echo "✅ EA tasks imported successfully!"
    else
        echo "⚠️  EA_Tasks.xlsx not found. Skipping import."
    fi
else
    echo "✅ Data already exists ($TASK_COUNT tasks). Skipping import."
fi

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << END
from tasks.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@coopbank.co.ke', 'CoopBank2025!')
    print('✅ Superuser created: admin / CoopBank2025!')
else:
    print('✅ Superuser already exists')
END

# Start Django server
echo "🚀 Starting Django server..."
python manage.py runserver 0.0.0.0:8000