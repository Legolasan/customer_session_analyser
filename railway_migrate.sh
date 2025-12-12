#!/bin/bash
# Railway deployment migration script
# This script can be added to Railway build commands or run manually

set -e  # Exit on error

echo "🚀 Starting Railway database migration..."

# Check if we're in production
if [ "$RAILWAY_ENVIRONMENT" = "production" ]; then
    echo "⚠️  PRODUCTION environment detected"
    echo "📋 Ensure you have:"
    echo "   1. Reviewed migration files"
    echo "   2. Tested migrations locally"
    echo "   3. Database backup available (Railway provides this)"
fi

# Set Flask app
export FLASK_APP=wsgi.py

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "❌ Error: migrations directory not found"
    echo "   Run 'flask db init' first"
    exit 1
fi

# Check current migration status
echo "📊 Current migration status:"
flask db current || echo "No migrations applied yet"

# Apply migrations
echo "🔄 Applying database migrations..."
flask db upgrade

if [ $? -eq 0 ]; then
    echo "✅ Migrations applied successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

echo "✨ Migration process completed"
