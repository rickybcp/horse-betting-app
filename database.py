# database.py
"""
Database initialization and configuration.
This file breaks the circular import by providing a single source of truth for database setup.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the database instance that will be shared across the app
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
def create_tables(app):
    """Create all database tables within app context."""
    with app.app_context():
        db.create_all()