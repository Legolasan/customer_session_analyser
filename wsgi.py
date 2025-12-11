"""
Main application entry point.
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use PORT environment variable (Railway provides this) or default to 5007 for local dev
    port = int(os.environ.get('PORT', 5007))
    # Disable debug mode in production (Railway sets RAILWAY_ENVIRONMENT)
    debug = os.environ.get('RAILWAY_ENVIRONMENT') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)

