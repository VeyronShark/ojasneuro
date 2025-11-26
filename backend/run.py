"""Entry point for running the Flask development server.

This module creates and runs the Flask application with all blueprints
registered and CORS configured for frontend integration.

Usage:
    python run.py
    
Environment Variables:
    FLASK_ENV: Configuration environment ('development', 'production', 'testing')
    PORT: Port to run the server on (default: 5000)
"""
import os
from app import create_app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    print(f"Debug mode: {debug}")
    print("Registered blueprints:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
