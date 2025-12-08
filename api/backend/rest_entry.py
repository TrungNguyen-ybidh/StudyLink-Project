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

# Student Routes - Import from student_routes.py (not maya_routes.py)
# Make this optional in case the file doesn't have all the blueprints yet
try:
    from backend.studylink.student.student_routes import calendar, reminder, grades, workload, events, courses
    HAS_STUDENT_ROUTES = True
except ImportError as e:
    print(f"Warning: Could not import student routes: {e}")
    HAS_STUDENT_ROUTES = False
    calendar = reminder = grades = workload = events = courses = None

# System Admin Routes
from backend.studylink.System_Admin.admin_routes import admin

# Optional: Generic demo routes (can be removed if not needed)
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

    # Load environment variables
    api_dir = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(api_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        app.logger.info(f'Loaded .env file from: {env_path}')
    else:
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

    # Secret key
    app.config["SECRET_KEY"] = get_env_var("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database configuration
    app.config["MYSQL_DATABASE_USER"] = get_env_var("DB_USER")
    app.config["MYSQL_DATABASE_PASSWORD"] = get_env_var("MYSQL_ROOT_PASSWORD")
    app.config["MYSQL_DATABASE_HOST"] = get_env_var("DB_HOST")
    app.config["MYSQL_DATABASE_PORT"] = int(get_env_var("DB_PORT"))
    app.config["MYSQL_DATABASE_DB"] = get_env_var("DB_NAME")

    # DEBUG: Print what we're actually using
    app.logger.info(f"DB_HOST = {app.config['MYSQL_DATABASE_HOST']}")
    app.logger.info(f"DB_PORT = {app.config['MYSQL_DATABASE_PORT']}")

    # Initialize the database
    app.logger.info("current_app(): starting the database connection")
    db.init_app(app)

    # Register blueprints
    app.logger.info("create_app(): registering blueprints with Flask app object.")
    
    # =========================================================================
    # REGISTER STUDYLINK BLUEPRINTS
    # =========================================================================
    
    # Data Analyst Routes (Persona 1: Jordan Lee)
    app.register_blueprint(analyst, url_prefix='/analyst')
    app.register_blueprint(metrics, url_prefix='/data')
    app.register_blueprint(datasets)  # No prefix, routes start with /datasets
    
    # Advisor Routes
    app.register_blueprint(advisor_bp)
    
    # Student Routes (only if successfully imported)
    if HAS_STUDENT_ROUTES:
        app.register_blueprint(calendar, url_prefix='/student')
        app.register_blueprint(reminder, url_prefix='/student')
        app.register_blueprint(grades, url_prefix='/student')
        app.register_blueprint(workload, url_prefix='/student')
        app.register_blueprint(events, url_prefix='/student')
        app.register_blueprint(courses, url_prefix='/student')
        app.logger.info("Registered student routes")
    else:
        app.logger.warning("Student routes not available, skipping registration")
    
    # System Admin Routes
    app.register_blueprint(admin)
    
    # Optional: Generic demo routes
    if HAS_SIMPLE_ROUTES and simple_routes:
        app.register_blueprint(simple_routes)
        app.logger.info("Registered simple_routes blueprint")

    return app

def setup_logging(app):
    pass