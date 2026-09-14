"""
Database initialization script for Anya.

Usage:
    python init_db.py          # Creates tables if they do not exist
    python init_db.py --reset  # Drops existing tables and recreates from scratch
"""

import sys
from app import create_app
from models import db

def init_database(reset=False):
    app = create_app()
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Target database URI: {db_uri}")

        if reset:
            print("Dropping existing tables (--reset specified)...")
            db.drop_all()

        print("Creating tables...")
        db.create_all()

        # Reflect created tables to confirm
        tables = db.metadata.tables.keys()
        print(f"Successfully initialized tables: {', '.join(sorted(tables))}")

if __name__ == '__main__':
    reset_flag = '--reset' in sys.argv
    init_database(reset=reset_flag)

