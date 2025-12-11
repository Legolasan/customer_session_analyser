# Customer Session Analyzer

A Flask-based web application for analyzing and managing customer session data. The application allows users to upload, parse, and visualize customer session information including customer details, regions, session counts, data sources, destinations, and time consumption metrics.

## Project Scope

This application provides a comprehensive solution for:

- **Data Upload**: Accept customer session data via text format or form-based input
- **Data Parsing**: Automatically parse structured text data into database records
- **Analytics & Insights**: Generate visualizations and statistics from session data
- **Reporting**: View tabular reports of all customer sessions
- **API Access**: RESTful API endpoints for programmatic access

### Key Features

- 📊 Interactive dashboards with visualizations
- 📝 Multiple input methods (text parsing and form-based)
- 🔍 Duplicate customer detection
- 📈 Time consumption tracking and analysis
- 🌍 Region and source/destination distribution analysis
- 🔌 RESTful API for integration
- 🗄️ Database-backed data persistence
- 🔐 Authentication system (admin-only data input, public read access)

## Project Structure

```
customer_session_analyzer/
├── app/
│   ├── __init__.py          # Flask app factory and configuration
│   ├── models.py            # Database models (CustomerSession)
│   ├── parser.py            # Text parsing logic for session data
│   ├── routes.py            # Flask routes and API endpoints
│   ├── analytics.py         # Analytics and insights generation
│   ├── auth.py              # Authentication helpers (User class)
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html        # Base template
│       ├── index.html       # Home/dashboard page
│       ├── input.html       # Form-based input page
│       ├── insights.html    # Analytics and visualizations
│       ├── reports.html     # Tabular reports
│       └── login.html       # Login page
├── wsgi.py                  # Application entry point (WSGI)
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Core Components

- **`app/__init__.py`**: Application factory pattern, database initialization, and configuration management
- **`app/models.py`**: SQLAlchemy model for `CustomerSession` with fields for customer, region, sessions, source, destination, time_consumed, and observations
- **`app/parser.py`**: Text parser that extracts structured data from formatted text input
- **`app/routes.py`**: All Flask routes including web pages and REST API endpoints
- **`app/analytics.py`**: Business logic for generating insights, statistics, and aggregations

## Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Legolasan/customer_session_analyser.git
   cd customer_session_analyser
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional for local dev)
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///customer_sessions.db
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```
   
   **Note**: For local development, you can skip `ADMIN_USERNAME` and `ADMIN_PASSWORD` if you don't need authentication. However, input features will be inaccessible without these credentials.

5. **Run the application**
   ```bash
   python wsgi.py
   ```

   The application will be available at `http://localhost:5007`

### Local Database

By default, the application uses SQLite for local development. The database file (`customer_sessions.db`) will be created automatically on first run.

## Railway Deployment

### Prerequisites

- Railway account ([railway.app](https://railway.app))
- GitHub account with the repository pushed

### Deployment Steps

1. **Create a New Project on Railway**
   - Go to [railway.app](https://railway.app) and sign in
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `customer_session_analyser` repository

2. **Add PostgreSQL Database**
   - In your Railway project dashboard, click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway will automatically provision a PostgreSQL database
   - The `DATABASE_URL` environment variable will be automatically set

3. **Configure Environment Variables**
   - Go to the "Variables" tab in your Railway project
   - Add the following variables:
     ```
     SECRET_KEY=<generate-a-secure-random-string>
     RAILWAY_ENVIRONMENT=production
     ADMIN_USERNAME=<your-admin-username>
     ADMIN_PASSWORD=<your-secure-password>
     ```
   - To generate a secure SECRET_KEY, run:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - **Important**: Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` to enable authentication. Without these, input features will be inaccessible.

4. **Deploy**
   - Railway will automatically detect the `Procfile` and deploy your application
   - The deployment process will:
     - Install dependencies from `requirements.txt`
     - Use gunicorn (via Procfile) to run the application
     - Automatically create database tables on first run
   - Railway will provide a public URL for your application

5. **Verify Deployment**
   - Visit the provided Railway URL
   - The application should be accessible over the internet
   - Database tables will be created automatically

### Railway Configuration Files

- **`Procfile`**: Specifies how Railway should run your application
  ```
  web: gunicorn wsgi:app --bind 0.0.0.0:$PORT
  ```

- **`requirements.txt`**: Lists all Python dependencies including `gunicorn` for production

- **`wsgi.py`**: Configured to use Railway's `PORT` environment variable and disable debug mode in production

### Database Migration (Optional)

If you want to use Flask-Migrate for database versioning:

```bash
# In Railway's console or using Railway CLI
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## API Endpoints

### Web Pages

- `GET /` - Home page dashboard (public)
- `GET /login` - Login page
- `GET /logout` - Logout (requires authentication)
- `GET /input` - Form-based input page (requires authentication)
- `GET /insights` - Analytics and visualizations page (public)
- `GET /reports` - Tabular reports page (public)

### REST API

- `POST /upload` - Upload session data via form (text format) - **Requires authentication**
- `POST /form-upload` - Upload session data via form fields - **Requires authentication**
- `POST /api/upload` - API endpoint for uploading session data (JSON) - **Requires authentication**
- `GET /api/insights` - Get analytics data (JSON) - **Public**
- `GET /api/sessions` - Get all sessions (JSON) - **Public**
- `GET /api/sessions/<id>` - Get a specific session by ID - **Public**
- `DELETE /api/sessions/<id>` - Delete a session by ID - **Requires authentication**

### Example API Usage

**Upload session data:**
```bash
curl -X POST http://your-app-url/api/upload \
  -H "Content-Type: application/json" \
  -d '{
    "session_data": "Customer: example.com\nRegion: US\nSessions: 10\nSource: API\nDestination: BQ"
  }'
```

**Get insights:**
```bash
curl http://your-app-url/api/insights
```

**Get all sessions:**
```bash
curl http://your-app-url/api/sessions
```

## Data Format

The application accepts customer session data in the following text format:

```
Customer: mediconas.cz [15 mins]
Region: EU
Sessions: 5
Source: FB Pages
Destination: BQ
Time Consumed: 15 mins
Observation: Additional notes or observations here
```

**Required Fields:**
- Customer
- Region
- Sessions (integer)
- Source
- Destination

**Optional Fields:**
- Time Consumed (1-120 minutes)
- Observation (text)

## Technology Stack

- **Backend**: Flask 3.0.0
- **Authentication**: Flask-Login 0.6.3
- **Database**: SQLAlchemy (SQLite for local, PostgreSQL for production)
- **Migrations**: Flask-Migrate
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **Production Server**: Gunicorn
- **Templates**: Jinja2

## Environment Variables

| Variable | Description | Default (Local) | Required (Production) |
|----------|-------------|-----------------|----------------------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` | Yes |
| `DATABASE_URL` | Database connection string | `sqlite:///customer_sessions.db` | Auto-set by Railway |
| `PORT` | Server port | `5007` | Auto-set by Railway |
| `RAILWAY_ENVIRONMENT` | Environment identifier | Not set | Set to `production` |
| `ADMIN_USERNAME` | Admin username for authentication | `admin` | Yes (for input features) |
| `ADMIN_PASSWORD` | Admin password for authentication | Not set | Yes (for input features) |

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors on Railway:
- Verify that PostgreSQL service is added to your Railway project
- Check that `DATABASE_URL` is automatically set (should be visible in Variables tab)
- Ensure the database service is running

### Port Issues

The application automatically uses Railway's `PORT` environment variable. No manual configuration needed.

### Debug Mode

Debug mode is automatically disabled in production when `RAILWAY_ENVIRONMENT=production` is set.

### Authentication Issues

If you cannot access input features:
- Verify that `ADMIN_USERNAME` and `ADMIN_PASSWORD` are set in environment variables
- Check that you're using the correct credentials
- Ensure cookies are enabled in your browser
- Try logging out and logging back in

**Note**: Dashboard, Insights, and Reports are publicly accessible. Only data input and modification features require authentication.

## Authentication

The application uses Flask-Login for session-based authentication. 

### Access Levels

- **Public Access**: Dashboard, Insights, Reports, and read-only API endpoints
- **Admin Access Required**: Input pages, data upload endpoints, and delete operations

### Setting Up Authentication

1. **Set Environment Variables**:
   ```env
   ADMIN_USERNAME=your-username
   ADMIN_PASSWORD=your-secure-password
   ```

2. **Login**:
   - Navigate to the Login page (link in navbar)
   - Enter your admin credentials
   - You'll be redirected to the dashboard after successful login

3. **Logout**:
   - Click "Logout (Admin)" in the navbar
   - Your session will be cleared

### Security Notes

- Passwords are stored in environment variables (never in code)
- Sessions are managed via secure cookies
- API endpoints return JSON 401 errors when authentication is required
- Input features are visually disabled for non-authenticated users

## License

This project is open source and available for use.

## Support

For issues or questions, please open an issue on the GitHub repository.
