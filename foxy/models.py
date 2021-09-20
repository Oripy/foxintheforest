from datetime import datetime
from foxy import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    first_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    second_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    first_player = db.relationship("User", foreign_keys=[first_player_id])
    second_player = db.relationship("User", foreign_keys=[second_player_id])
    status = db.Column(db.Integer, nullable=False, default=0)

    game = db.Column(db.String(1000))

    def __repr__(self):
        status = ["created", "started", "finished"][self.status]
        return f"Games('{self.date_created}', '{self.first_player}', '{self.second_player}', {status})"
