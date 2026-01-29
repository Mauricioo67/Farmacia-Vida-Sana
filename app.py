from flask import Flask, redirect, url_for
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize CORS
    CORS(app)

    # Register Blueprints
    from controllers.auth import auth_bp
    from controllers.main import main_bp
    from controllers.products import products_bp
    from controllers.products_api import products_api_bp
    from controllers.api_util import api_util_bp
    from controllers.clients import clients_bp
    from controllers.sales import sales_bp
    from controllers.categories import categories_bp
    from controllers.reports import reports_bp
    from controllers.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    # Registra products con prefijo /products para rutas web
    app.register_blueprint(products_bp, url_prefix='/products')
    # Registra API products separadamente
    app.register_blueprint(products_api_bp)
    app.register_blueprint(api_util_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(chatbot_bp)

    @app.route('/')
    def index():
        return redirect(url_for('main.dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
