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
    # Initialize database on first run
    from backend.database import init_db
    init_db()
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

