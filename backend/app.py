import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from models import db
from routes import api_bp

# Load environment variables from .env if present
load_dotenv()

def create_app(test_config=None):
    """
    Application factory pattern.
    Configures and returns the Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance directory exists for SQLite database storage
    os.makedirs(app.instance_path, exist_ok=True)

    # Default configuration
    default_db_path = os.path.join(app.instance_path, 'anya.db')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f"sqlite:///{default_db_path}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Register API routes Blueprint
    app.register_blueprint(api_bp)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

