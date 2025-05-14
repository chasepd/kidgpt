from flask import Flask
from datetime import timedelta
from app.config.settings import SECRET_KEY
from app.core.ai_clients.openai_client import OpenAIClient

def create_app(config=None):
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configure the Flask application
    if config is not None:
        app.config.from_object(config)
    
    # Configure session
    app.permanent_session_lifetime = timedelta(days=30)
    app.secret_key = SECRET_KEY

    # Initialize AI client (now loads key from DB)
    app.ai_client = OpenAIClient(banned_keywords=[])
    
    # Register routes
    from app.api import routes
    app.register_blueprint(routes.bp)
    
    return app 