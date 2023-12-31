from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from models import User, TriviaPack, Question, Scoreboard, Like
with app.app_context():
    db.create_all()


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

from views import *

if __name__ == '__main__':
    app.run(debug=True)
