from flask import Flask
from .routes import main
from .database import db

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    

    db.init_app(app)
    app.register_blueprint(main)

    return app
