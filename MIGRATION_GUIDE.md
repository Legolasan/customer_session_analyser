# Database Migration Guide

This guide explains how to safely manage database schema changes for the Customer Session Analyzer application using Flask-Migrate.

## Table of Contents

- [Overview](#overview)
- [Migration Workflow](#migration-workflow)
- [Adding New Fields](#adding-new-fields)
- [Railway Deployment](#railway-deployment)
- [Rollback Procedures](#rollback-procedures)
- [Safety Features](#safety-features)
- [Troubleshooting](#troubleshooting)

## Overview

This application uses **Flask-Migrate** (built on Alembic) to manage database schema changes safely. Migrations provide:

- ✅ **Version control** for schema changes
- ✅ **Reviewable SQL** before applying changes
- ✅ **Rollback capability** if something goes wrong
- ✅ **Production safety** - no automatic table creation/destruction

### Key Principles

1. **Never** use `db.create_all()` or `db.drop_all()` in production
2. **Always** review migration files before applying
3. **Test** migrations on local database first
4. **Backup** production database before major migrations
5. Migrations are **additive by default** - adding columns is safe, removing requires caution

## Migration Workflow

### Initial Setup (Already Done)

The migrations directory has been initialized and the initial migration created. The current schema is captured in:
- `migrations/versions/001_initial_migration_customer_sessions.py`

### Making Schema Changes

When you need to modify the database schema:

#### Step 1: Update the Model

Edit `app/models.py` to add, modify, or remove fields:

```python
class CustomerSession(db.Model):
    # ... existing fields ...
    new_field = db.Column(db.String(100), nullable=True)  # New field
```

#### Step 2: Generate Migration

Create a new migration file:

```bash
export FLASK_APP=wsgi.py
flask db migrate -m "Add new_field to customer_sessions"
```

This creates a new file in `migrations/versions/` with a timestamp and description.

#### Step 3: Review Migration File

**CRITICAL**: Always review the generated migration file before applying:

```bash
# Open the newly created migration file
cat migrations/versions/XXXX_add_new_field_to_customer_sessions.py
```

Check that:
- ✅ The migration only makes the changes you expect
- ✅ No unexpected table drops or data deletions
- ✅ Default values are set for NOT NULL fields (if adding to existing table)
- ✅ Indexes are created for new indexed fields

#### Step 4: Test Locally

Apply the migration to your local database:

```bash
# Using the helper script
python migrate_db.py upgrade

# Or directly
flask db upgrade
```

Verify the changes:
- Check that the table structure is correct
- Test that your application still works
- Verify data integrity

#### Step 5: Commit to Git

```bash
git add migrations/versions/XXXX_add_new_field_to_customer_sessions.py
git commit -m "Add migration for new_field"
```

**Important**: Always commit migration files with your code changes.

#### Step 6: Deploy to Railway

1. Push your changes to the repository
2. Railway will automatically deploy
3. Run migrations (see [Railway Deployment](#railway-deployment) below)

## Adding New Fields

### Adding a Nullable Field (Safest)

```python
# In app/models.py
new_field = db.Column(db.String(100), nullable=True)
```

This is the safest operation - no data loss risk.

### Adding a Non-Nullable Field

If you need to add a field that cannot be NULL:

```python
# Option 1: Provide a default value
new_field = db.Column(db.String(100), nullable=False, server_default='default_value')

# Option 2: Make it nullable first, then update data, then make it non-nullable
# (Requires two migrations)
```

**Best Practice**: Use a two-step migration:
1. Add field as nullable
2. Populate existing rows with data
3. Make field non-nullable

### Removing Fields

⚠️ **WARNING**: Removing fields will delete data. Always backup first.

```python
# Remove from model
# Then generate migration
flask db migrate -m "Remove deprecated_field"
```

Review the migration carefully - it will drop the column and all data in it.

## Railway Deployment

### Automatic Migration (Recommended)

Add to your Railway build command or use a release command:

```bash
# In Railway, set as "Release Command":
./railway_migrate.sh
```

Or manually in Railway console:

```bash
export FLASK_APP=wsgi.py
flask db upgrade
```

### Manual Migration

1. Connect to Railway via CLI or web console
2. Run the migration script:

```bash
./railway_migrate.sh
```

Or use the Python helper:

```bash
python migrate_db.py upgrade
```

### Pre-Deployment Checklist

Before deploying migrations to production:

- [ ] Migration files reviewed and tested locally
- [ ] Database backup available (Railway provides automatic backups)
- [ ] Rollback plan prepared
- [ ] Migration tested on staging environment (if available)
- [ ] Team notified of deployment

## Rollback Procedures

### Rollback Last Migration

```bash
# Using helper script
python migrate_db.py downgrade

# Or directly
flask db downgrade
```

### Rollback to Specific Revision

```bash
# First, check history
flask db history

# Then downgrade to specific revision
flask db downgrade <revision_id>
```

### Emergency Rollback

If a migration causes issues in production:

1. **Stop the application** (if possible)
2. **Restore from backup** (Railway provides automatic backups)
3. **Or rollback migration**:
   ```bash
   flask db downgrade
   ```
4. **Redeploy previous version** of code

## Safety Features

### Environment Checks

The application automatically:
- ✅ Only uses `db.create_all()` in development mode
- ✅ Relies on migrations in production
- ✅ Logs database operations for debugging

### Migration Validation

The `migrate_db.py` script:
- ✅ Checks environment before running migrations
- ✅ Prompts for confirmation in production
- ✅ Provides safety reminders

### Code Safeguards

The `app/__init__.py` includes:
- ✅ Environment-based table creation (dev only)
- ✅ Logging for database operations
- ✅ Protection against accidental `db.drop_all()`

## Troubleshooting

### Migration Conflicts

If you have migration conflicts:

```bash
# Check current status
flask db current

# Check history
flask db history

# Merge branches if needed
flask db merge -m "Merge migration branches"
```

### "Target database is not up to date"

This means your database schema doesn't match the migration history:

```bash
# Check what migrations are pending
flask db heads
flask db current

# Apply pending migrations
flask db upgrade
```

### "Can't locate revision identified by"

This usually means migration files are out of sync:

1. Check that all migration files are committed to git
2. Ensure you're on the latest code version
3. If needed, stamp the database to match:

```bash
flask db stamp head  # Mark database as up-to-date (use with caution)
```

### Database Connection Issues

If migrations fail due to connection:

1. Check `DATABASE_URL` environment variable
2. Verify database is accessible
3. Check Railway database status

## Best Practices

1. **One migration per feature** - Don't bundle multiple unrelated changes
2. **Descriptive names** - Use clear migration messages
3. **Test thoroughly** - Always test migrations locally first
4. **Review before applying** - Never blindly apply migrations
5. **Backup before major changes** - Especially for destructive operations
6. **Document breaking changes** - Note any API or data structure changes

## Quick Reference

```bash
# Initialize migrations (already done)
flask db init

# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Check current revision
flask db current

# View history
flask db history

# Using helper script
python migrate_db.py upgrade
python migrate_db.py downgrade
python migrate_db.py status
python migrate_db.py history
```

## Support

For issues or questions:
1. Check this guide first
2. Review Flask-Migrate documentation: https://flask-migrate.readthedocs.io/
3. Check Alembic documentation: https://alembic.sqlalchemy.org/

---

**Remember**: When in doubt, test locally first and always backup production data!
