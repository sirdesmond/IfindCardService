from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from config import config
from flask.ext.login import LoginManager

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
#login_manager.login_view = ''

def create_app(config_name):
	app = Flask(__name__)
	mail.init_app(app)
	app.config.from_object(config[config_name])
	db.init_app(app)
	login_manager.init_app(app)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .api_1_0 import api as api_blueprint
	app.register_blueprint(api_blueprint,url_prefix='/api/v1.0')

	return app
