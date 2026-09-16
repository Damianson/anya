import os
from flask import Flask, send_from_directory, jsonify
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
    Supports serving both the API and the compiled Vite frontend SPA.
    """
    # Determine frontend build directory (if present)
    frontend_dist = os.environ.get(
        'FRONTEND_DIST',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/dist'))
    )
    static_folder = frontend_dist if os.path.isdir(frontend_dist) else None

    app = Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='',
        instance_relative_config=True
    )

    # Ensure the instance directory exists for SQLite database storage
    os.makedirs(app.instance_path, exist_ok=True)

    # Database configuration & normalization for Render PostgreSQL
    default_db_path = os.path.join(app.instance_path, 'anya.db')
    db_uri = os.environ.get('DATABASE_URL')
    if not db_uri:
        db_uri = f"sqlite:///{default_db_path}"
    elif db_uri.startswith('sqlite:///instance/'):
        db_filename = db_uri.replace('sqlite:///instance/', '')
        db_uri = f"sqlite:///{os.path.join(app.instance_path, db_filename)}"
    elif db_uri.startswith('postgres://'):
        # SQLAlchemy 2.0 requires postgresql:// instead of legacy postgres://
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Initialize database tables and auto-seed if empty on first boot
    with app.app_context():
        try:
            db.create_all()
            from models import Incident
            if Incident.query.first() is None:
                from seed_db import populate_seed_data
                populate_seed_data(reset=False)
                app.logger.info("Database auto-seeded with benchmark crisis scenarios.")
        except Exception as e:
            app.logger.warning(f"Database startup auto-init notice: {e}")

    # Register API routes Blueprint
    app.register_blueprint(api_bp)

    # Health check endpoint for Render zero-downtime deployment monitoring
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': 'anya-crisis-platform',
            'database': 'connected' if db_uri else 'unconfigured'
        }), 200

    # Catch-all route to serve the Vite frontend SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if app.static_folder and os.path.isdir(app.static_folder):
            target_file = os.path.join(app.static_folder, path)
            if path and os.path.exists(target_file) and not os.path.isdir(target_file):
                return send_from_directory(app.static_folder, path)
            index_file = os.path.join(app.static_folder, 'index.html')
            if os.path.exists(index_file):
                return send_from_directory(app.static_folder, 'index.html')
        return jsonify({
            'service': 'Anya Crisis API',
            'status': 'operational',
            'endpoints': ['/incidents', '/reports', '/webhooks/sms', '/health']
        }), 200

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug)
