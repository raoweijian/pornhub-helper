import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter

from config import config


db = SQLAlchemy()


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.url_map.converters['regex'] = RegexConverter
    config[config_name].init_app(app)
    db.init_app(app)
    # 附加路由和自定义的错误页面

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app


flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
