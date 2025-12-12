#!/usr/bin/env python3
"""
Safe database migration helper script.

This script provides a safe way to run database migrations with
validation and backup reminders.

Usage:
    python migrate_db.py upgrade    # Apply all pending migrations
    python migrate_db.py downgrade  # Rollback last migration
    python migrate_db.py status     # Show current migration status
    python migrate_db.py history    # Show migration history
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask app
os.environ['FLASK_APP'] = 'wsgi.py'

def check_environment():
    """Check if we're in a safe environment for migrations."""
    is_production = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    
    if is_production:
        print("⚠️  WARNING: Running in PRODUCTION environment")
        print("📋 Pre-migration checklist:")
        print("   1. Database backup created? (Railway provides automatic backups)")
        print("   2. Migration files reviewed?")
        print("   3. Tested on staging/local environment?")
        print("   4. Rollback plan ready?")
        
        response = input("\nContinue with migration? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Migration cancelled for safety.")
            sys.exit(1)
    else:
        print("✅ Development environment detected - proceeding safely")

def run_migration_command(command):
    """Run a Flask-Migrate command."""
    import subprocess
    
    cmd = ['flask', 'db', command]
    
    if command == 'upgrade':
        check_environment()
        print("\n🔄 Applying database migrations...")
    elif command == 'downgrade':
        check_environment()
        print("\n⏪ Rolling back last migration...")
    elif command == 'status':
        print("\n📊 Checking migration status...")
    elif command == 'history':
        print("\n📜 Migration history:")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("\n✅ Migration command completed successfully")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Migration command failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: Flask-Migrate not found. Make sure you're in a virtual environment")
        print("   and have installed requirements: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable commands:")
        print("  upgrade   - Apply all pending migrations")
        print("  downgrade - Rollback last migration")
        print("  status    - Show current migration status")
        print("  history   - Show migration history")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    valid_commands = ['upgrade', 'downgrade', 'status', 'history']
    if command not in valid_commands:
        print(f"❌ Invalid command: {command}")
        print(f"Valid commands: {', '.join(valid_commands)}")
        sys.exit(1)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    run_migration_command(command)

if __name__ == '__main__':
    main()
