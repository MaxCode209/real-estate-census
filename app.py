"""Main Flask application."""
from flask import Flask, render_template
from flask_cors import CORS
from backend.routes import api
from config.config import Config

app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app)

# Register API blueprint
app.register_blueprint(api)

@app.route('/api/version')
def api_version():
    """Confirm API code version (e.g. school_source in /api/schools/address)."""
    return {'ok': True, 'school_source_in_schools_address': True}

@app.route('/')
def index():
    """Serve the main map interface."""
    return render_template('index.html', 
                         google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)

@app.route('/test')
def test():
    """Test connection page."""
    return render_template('test.html')

if __name__ == '__main__':
    import os
    print("[App] Running from:", os.getcwd())
    # Initialize database on first run
    from backend.database import init_db, engine
    init_db()
    # Confirm we're using Transaction mode (6543) for Supabase - avoids "max clients" error
    url_str = str(engine.url)
    if "pooler.supabase.com" in url_str and ":5432" in url_str:
        raise SystemExit("BUG: Still using port 5432 (Session mode). Use port 6543. Check .env and backend/database.py.")
    if "pooler.supabase.com" in url_str:
        print("[DB] Using Supabase pooler port 6543 (Transaction mode) - OK")
    # use_reloader=False so the same process handles requests and print() shows in terminal
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000, use_reloader=False)

