"""Implementation of Fox in the Forest, a trick-taking game for two players
    designed by Joshua Buergel

    Complete website with frontend and server using Flask, SocketIO and vanilla JS
"""

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
import redis
from rq import Queue

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = _l('Please log in to access this page.')
login_manager.login_message_category = 'info'
socketio = SocketIO(app, message_queue='redis://')
babel = Babel(app)
redis_server = redis.Redis()
redis_queue = Queue(connection=redis_server)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

from foxy import routes
