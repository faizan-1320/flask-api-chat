from flask import Flask,jsonify,g
from .chat import chat_bp
from flask_cors import CORS
from .socket import socketio
import os
import mysql.connector
from flask_jwt_extended import JWTManager
from .database import get_db,close_db
from .authentication import auth_bp
from datetime import timedelta
from flask_mail import Mail, Message    

app = Flask(__name__)
def create_app():
    CORS(app)
    socketio.init_app(app,cors_allowed_origins="*")
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret" 

    @app.before_request
    def before_request():
        print(" -----------------------> Before Request")
        try:
            
            g.db = get_db()
        except:
            return jsonify({'error':'Database connection failed'})
        
    @app.after_request
    def after_request(response):
        print("-----------------------> After Request")
        try:
            close_db()
        except:
            return jsonify({'error':'Database connection failed'})
        return response
    
    app.register_blueprint(chat_bp, url_prefix='/v1/chat')
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')

    socketio.init_app(app) 
    app.config['JWT_SECRET_KEY']=os.environ['JWT_SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(days=1)    

    jwt = JWTManager(app)

    

    return app

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)