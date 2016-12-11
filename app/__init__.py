from flask import Flask
#from flask_bootstrap import Bootstrap
from flask_material import Material
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import config

#bootstrap = Bootstrap()
material = Material()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #bootstrap.init_app(app)
    material.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .english import english as english_blueprint
    app.register_blueprint(english_blueprint, url_prefix='/e')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
