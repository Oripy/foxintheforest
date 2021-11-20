from flask import json
# from flask_socketio import emit

from foxy import random_ai
from foxy import good_ai
from foxy.models import Games
from foxy import foxintheforest, db
from foxy.routes import socketio

AI_dict = {"TheBad": random_ai, "TheGood": good_ai}

def next_ai_move(ai_name, game_id):
    game_data = Games.query.filter_by(match_id=game_id).order_by(Games.date_created.desc()).first()
    game_state = json.loads(game_data.game)
    ai_play = AI_dict[ai_name].ai_play(foxintheforest.get_player_game(game_state, 1))
    game_state = foxintheforest.play(game_state, ai_play)
    state = foxintheforest.get_state_from_game(game_state)
    if len(state["discards"][0]) + len(state["discards"][1]) == 26:
        game_data.status = 2
    game_data.game = json.dumps(game_state)
    game_data.lock = False
    db.session.commit()
    socketio.emit("game changed", json.dumps({}), room=game_id)
