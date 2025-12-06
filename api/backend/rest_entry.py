from flask import Flask
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

from backend.db_connection import db

# =========================================================================
# STUDYLINK BLUEPRINT IMPORTS
# =========================================================================

# Data Analyst Routes (Persona 1: Jordan Lee)
from backend.studylink.data_analyst.analyst_routes import analyst
from backend.studylink.data_analyst.metric_routes import metrics
from backend.studylink.data_analyst.dataset_routes import datasets

# Advisor Routes
from backend.studylink.advisor.advisor_routes import advisor_bp

# Student Routes (Maya)
from backend.studylink.student.maya_routes import calendar, reminder, grades, workload, events, courses

# System Admin Routes
from backend.studylink.System_Admin.admin_routes import admin

# Optional: Generic demo routes (can be removed if not needed)
# Making this optional to avoid errors if the module doesn't exist
try:
    from backend.simple.simple_routes import simple_routes
    HAS_SIMPLE_ROUTES = True
except ImportError:
    HAS_SIMPLE_ROUTES = False
    simple_routes = None

def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Configure file logging if needed
    #   Uncomment the code in the setup_logging function
    # setup_logging(app) 

    # Load environment variables
    # This function reads all the values from inside
    # the .env file (in the api folder) so they
    # are available in this file.  See the MySQL setup
    # commands below to see how they're being used.
    # Try to load from api/.env first, then fallback to parent directory
    api_dir = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(api_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        app.logger.info(f'Loaded .env file from: {env_path}')
    else:
        # Fallback to current directory or parent
        load_dotenv()
        app.logger.warning(f'.env file not found at {env_path}. Using system environment variables or defaults.')

    # Helper function to safely get environment variables
    def get_env_var(var_name, default_value=None):
        value = os.getenv(var_name)
        if value is None:
            if default_value is not None:
                return default_value
            raise ValueError(f"Environment variable '{var_name}' not set. Please check your .env file.")
        return value.strip()

    # secret key that will be used for securely signing the session
    # cookie and can be used for any other security related needs by
    # extensions or your application
    app.config["SECRET_KEY"] = get_env_var("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database configuration - these are for the DB object to be able to connect to MySQL
    app.config["MYSQL_DATABASE_USER"] = get_env_var("DB_USER")
    app.config["MYSQL_DATABASE_PASSWORD"] = get_env_var("MYSQL_ROOT_PASSWORD")
    app.config["MYSQL_DATABASE_HOST"] = get_env_var("DB_HOST")
    app.config["MYSQL_DATABASE_PORT"] = int(get_env_var("DB_PORT"))
    app.config["MYSQL_DATABASE_DB"] = get_env_var("DB_NAME")

    # Initialize the database object with the settings above.
    app.logger.info("current_app(): starting the database connection")
    db.init_app(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each
    app.logger.info("create_app(): registering blueprints with Flask app object.")
    
    # =========================================================================
    # REGISTER STUDYLINK BLUEPRINTS
    # =========================================================================
    
    # Data Analyst Routes (Persona 1: Jordan Lee)
    # Analyst routes: dashboard, engagement, student reports
    # URL prefix: /analyst
    # Example endpoints:
    #   GET /analyst/dashboard
    #   GET /analyst/engagement
    #   GET /analyst/students
    #   GET /analyst/students/<id>/report
    app.register_blueprint(analyst, url_prefix='/analyst')
    
    # Metrics routes: CRUD for metrics, data errors, assignments
    # URL prefix: /data
    # Example endpoints:
    #   GET/POST /data/metrics
    #   GET/PUT/DELETE /data/metrics/<id>
    #   GET/POST/PUT /data/data-errors
    #   GET/PUT /data/assignments
    app.register_blueprint(metrics, url_prefix='/data')
    
    # Dataset routes: dataset management, uploads, archiving
    # URL prefix: /datasets (no prefix, routes start with /datasets)
    # Example endpoints:
    #   GET /datasets
    #   POST /datasets
    #   GET /datasets/<id>
    #   PUT /datasets/<id>
    #   DELETE /datasets/<id>
    app.register_blueprint(datasets)
    
    # Advisor Routes
    # URL prefix: /api/advisor (already included in blueprint definition)
    # Example endpoints:
    #   GET /api/advisor/
    app.register_blueprint(advisor_bp)
    
    # Student Routes (Maya)
    # URL prefix: /student
    # Example endpoints:
    #   GET /student/calendar
    #   GET /student/reminder
    #   GET /student/grades
    #   GET /student/workload
    #   GET /student/events
    #   GET /student/courses
    app.register_blueprint(calendar, url_prefix='/student')
    app.register_blueprint(reminder, url_prefix='/student')
    app.register_blueprint(grades, url_prefix='/student')
    app.register_blueprint(workload, url_prefix='/student')
    app.register_blueprint(events, url_prefix='/student')
    app.register_blueprint(courses, url_prefix='/student')
    
    # System Admin Routes
    # URL prefix: /admin
    app.register_blueprint(admin)
    
    # Optional: Generic demo routes (for testing/development)
    # Can be removed if not needed
    if HAS_SIMPLE_ROUTES and simple_routes:
        app.register_blueprint(simple_routes)
        app.logger.info("Registered simple_routes blueprint")
    else:
        app.logger.info("simple_routes not available, skipping registration")

    # Don't forget to return the app object
    return app

def setup_logging(app):
    """
    Configure logging for the Flask application in both files and console (Docker Desktop for this project)
    
    Args:
        app: Flask application instance to configure logging for
    """
    # if not os.path.exists('logs'):
    #     os.mkdir('logs')

    ## Set up FILE HANDLER for all levels
    # file_handler = RotatingFileHandler(
    #     'logs/api.log',
    #     maxBytes=10240,
    #     backupCount=10
    # )
    # file_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    # ))
    
    # Make sure we are capturing all levels of logging into the log files. 
    # file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    # app.logger.addHandler(file_handler)

    # ## Set up CONSOLE HANDLER for all levels
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s'
    # ))
    # Debug level capture makes sure that all log levels are captured
    # console_handler.setLevel(logging.DEBUG)
    # app.logger.addHandler(console_handler)
    pass
    
    