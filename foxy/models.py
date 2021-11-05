"""Define the database models for the Fox in the Forest Flask app"""
from datetime import datetime

from flask_login import UserMixin

from foxy import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Define where LoginManager should look for users in the database"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Users database
        id: unique auto generated identification number
        username: unique User name
        password: hashed password
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Matches(db.Model):
    """Matches database
        id: unique auto generated identification number
        name: user submitted game name string
        date_created: date of game creation
        first_player_id: id of first player (user that created the game)
        second_player_id: id of second player (could be an AI)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    first_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    second_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    first_player = db.relationship("User", foreign_keys=[first_player_id])
    second_player = db.relationship("User", foreign_keys=[second_player_id])
    status = db.Column(db.Integer, nullable=False, default=0)
    score_first_player = db.Column(db.Integer, nullable=False, default=0)
    score_second_player = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        status = ["created", "started", "finished"][self.status]
        return (f"Matches('{self.date_created}', '{self.first_player}', "
                f"'{self.second_player}', {status})")

class Games(db.Model):
    """Games database
        id: unique auto generated identification number
        date_created: date of game creation
        match_id: id of the linked match
        status: int
            0 = created (waiting for second user)
            1 = started
            2 = finished
        game: game state json dump
    """
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    match = db.relationship("Matches", foreign_keys=[match_id])
    status = db.Column(db.Integer, nullable=False, default=0)
    game = db.Column(db.String(1000))

    def __repr__(self):
        status = ["created", "started", "finished"][self.status]
        return (f"Games('{self.match_id}', '{self.match_id.first_player}', "
                f"'{self.match_id.second_player}', {status})")
