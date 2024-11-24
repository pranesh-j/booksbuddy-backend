#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
echo "Building the project..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py makemigrations api
python manage.py migrate
python manage.py migrate api

# Don't start gunicorn here - let Render handle it 
# Start gunicorn
echo "Starting gunicorn..."
gunicorn booksbuddy_backend.wsgi:application 