from flask import Flask, jsonify
from .api.server import api_blueprint
from .routes.routes import routes_bp
from .worker.urls import worker_bp

def create_app():
    """Application factory pattern for Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['DEBUG'] = True
    
    # Register blueprints with proper URL prefixes
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    app.register_blueprint(routes_bp, url_prefix='/')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found',
            'available_endpoints': [
                'GET / - API documentation',
                'POST /enqueue - Enqueue package build',
                'GET /health - Health check',
                'GET /<package> - Get installer script',
                'GET /<package>@<version> - Get specific version installer',
                'GET /meta/<package> - Get package metadata',
                'GET /worker/builds - List all builds',
                'POST /worker/builds - Create new build',
                'GET /api/ - API welcome message'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong on our end'
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n PyBins Flask Application Starting...")
    print(" Python Package Freezer Service")
    print(" Available at: http://localhost:5000")
    print(" API Documentation: http://localhost:5000/\n")
    app.run(host='0.0.0.0', port=5000, debug=True)