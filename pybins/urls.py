from flask import Flask
from routes.routes import routes_bp
from .worker.urls import worker_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(worker_bp, url_prefix='/api')
app.register_blueprint(routes_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)