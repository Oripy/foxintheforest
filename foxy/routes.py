"""Route file for the Fox in the Forest server
    Flask routes:
        / or /home: Homepage
        /register: to register as a new user
        /login: to login as an existing user
        /logout: to log out the user
        /lobby: a view to
            create a new game,
            play on games where the login user is one of the player,
            join games created by other users
        /leaderboard: a list of all players with their overall results
        /new: create a new game
        /game: connect to an existing game
    SocketIO "routes":
        get game: returns the game state (with the point of view of the logged-in player)
        play: play a card
"""
from __future__ import annotations
from typing import Callable, Union
from flask import flash, render_template, url_for, request, json, redirect
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import disconnect, emit, join_room

from foxy import app, db, bcrypt, socketio
from foxy.forms import RegistrationForm, LoginForm
from foxy.models import User, Matches, Games
from foxy import foxintheforest
from foxy import random_ai
from foxy import good_ai

AI_dict = {"TheBad": random_ai, "TheGood": good_ai}

def authenticated_only(func: Callable) -> Callable:
    """Decorator to disconnect if user is not authenticated for socketio.on() functions"""
    def wrapper(*args, **kwargs) -> Union[Callable, None]:
        if not current_user.is_authenticated:
            disconnect()
            return None
        return func(*args, **kwargs)
    return wrapper

def flash_io(text: str, category: str = "info") -> None:
    """Send "message" to the client with the given category"""
    emit('message', json.dumps({"text": text, "category": category}))

def create_new_game(match_id):
    """Create a new game in the database"""
    game_state = json.dumps(foxintheforest.new_game())
    return Games(game=game_state, match_id=match_id, status=1)

@app.route("/")
@app.route("/home")
def main() -> str:
    """Returns the homepage"""
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Adds a new user to the Database"""
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Checks if login information is in the database and login the user"""
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back {form.username.data}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('lobby'))
        flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    """Logout the user"""
    logout_user()
    return redirect(url_for('main'))

@app.route("/lobby")
@login_required
def lobby():
    """A view to
        create a new game,
        play on games where the login user is one of the player,
        join games created by other users"""
    open_games = Matches.query.filter(
        (((Matches.first_player_id==None)|(Matches.second_player_id==None))&(Matches.status<2)))
    own_games = Matches.query.filter(
        (((Matches.first_player_id==current_user.id)|(Matches.second_player_id==current_user.id))&(Matches.status<2)))
    return render_template('lobby.html', open_games=open_games, own_games=own_games)

@app.route("/leaderboard", methods=['GET'])
def leaderboard():
    """List all players and their overall result"""
    finished_games = Matches.query.filter((Matches.status==2))
    player_list = {}
    for game in finished_games:
        if not game.first_player.username in player_list:
            player_list[game.first_player.username] = [0, 0]
        if not game.second_player.username in player_list:
            player_list[game.second_player.username] = [0, 0]
        if (game.score_first_player > game.score_second_player):
            player_list[game.first_player.username][0] += 1
            player_list[game.second_player.username][1] += 1
        else:
            player_list[game.first_player.username][1] += 1
            player_list[game.second_player.username][0] += 1
    board = []
    for player, values in player_list.items():
        ratio = values[0]/(values[0] + values[1])
        board.append([0, player, values[0], values[1], 100*ratio])
    board.sort(key=lambda x: -x[4])
    if (len(board) > 0):
        prev_ratio = board[0][4]
        prev_rank = 1
        for rank, line in enumerate(board):
            if prev_ratio != line[4]:
                prev_ratio = line[4]
                prev_rank = rank + 1
            line[0] = prev_rank
    return render_template('leaderboard.html', board=board)

@app.route("/new", methods=['POST'])
@login_required
def new():
    """Create a new game,
        if AI is given, adds the AI as the second player
        if successful returns the game page
        othewise redirects to the lobby"""
    if 'AI' in request.form:
        ai = User.query.filter_by(username=request.form['AI']).first()
        if ai:
            match_db = Matches(name=request.form['gamename'],
                               first_player_id=current_user.id,
                               second_player_id=ai.id, status=1)
            db.session.add(match_db)
            db.session.flush()
            game_db = create_new_game(match_db.id)
        else:
            flash('This AI does not exists.', 'danger')
            return redirect(url_for('lobby'))
    else:
        match_db = Matches(name=request.form['gamename'],
                           first_player_id=current_user.id,
                           status=1)
        db.session.add(match_db)
        db.session.flush()
        game_db = create_new_game(match_db.id)
    db.session.add(game_db)
    db.session.commit()
    return redirect(url_for('game', id=match_db.id))

@app.route("/game")
@login_required
def game():
    """Load the game page, if a spot is free, user joins the game"""
    game_id = request.args.get("id")
    game_state = Matches.query.filter_by(id=game_id).first()
    if game_state is None:
        flash('This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if game_state.first_player_id == current_user.id:
        return render_template('game.html', id=game_id,
            opponent=game_state.second_player.username
            if game_state.second_player is not None else None)
    if game_state.second_player_id == current_user.id:
        return render_template('game.html', id=game_id, opponent=game_state.first_player.username)
    if game_state.second_player_id is None:
        game_state.second_player_id = current_user.id
        game_state.status = 1
        db.session.commit()
        return render_template('game.html', id=game_id, opponent=game_state.first_player.username)
    flash('You are not a player in this game.', 'danger')
    return redirect(url_for('lobby'))

@socketio.on('get game')
@authenticated_only
def get_game(data):
    """Send the game state through socketio messages"""
    req = json.loads(data)
    game_id = req["id"]
    join_room(game_id)
    match_data = Matches.query.filter_by(id=game_id).first()
    game_data = Games.query.filter_by(match_id=game_id).order_by(Games.date_created.desc()).first()
    if game_data is None:
        flash_io('This game does not exists.', 'danger')
    elif match_data.first_player_id == current_user.id:
        player = 0
    elif match_data.second_player_id == current_user.id:
        player = 1
    else:
        flash_io('You are not a player in this game.', 'danger')
        return
    game_state = json.loads(game_data.game)
    emit("game", json.dumps(foxintheforest.get_player_game(game_state, player)))
    if match_data.second_player:
        if match_data.second_player.username in AI_dict.keys():
            state = foxintheforest.get_state_from_game(game_state)
            while state["current_player"] == 1 and game_data.status != 2 and not game_data.lock:
                game_data.lock = True
                db.session.commit()
                ai_play = AI_dict[match_data.second_player.username].ai_play(
                    foxintheforest.get_player_game(game_state, 1))
                game_state = foxintheforest.play(game_state, ai_play)
                state = foxintheforest.get_state_from_game(game_state)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game_data.status = 2
                game_data.game = json.dumps(game_state)
                game_data.lock = False
                db.session.commit()
                emit("game changed", json.dumps({}), room=game_id)
    if game_data.status == 2:
        state = foxintheforest.get_state_from_game(json.loads(game_data.game))
        match_data.score_first_player += state["score"][0]
        match_data.score_second_player += state["score"][1]
        emit("game ended", json.dumps({"score": state["score"], "discards": state["discards"]}))
        if (match_data.score_first_player >= 21 or match_data.score_second_player >= 21):
            match_data.status = 2
            emit("match ended", json.dumps({"score": [match_data.score_first_player,
                                                        match_data.score_second_player]}))
            flash_io('Game finished.', 'danger')
        else:
            db.session.add(create_new_game(game_id))
        db.session.commit()
    return

@socketio.on('play')
@authenticated_only
def play(data):
    """Play the given move and send info that game state changed to all players"""
    req = json.loads(data)
    card_played = None
    game_id = req["id"]
    player = req["player"]
    match_data = Matches.query.filter_by(id=game_id).first()
    game_data = Games.query.filter_by(match_id=game_id).order_by(Games.date_created.desc()).first()
    if game_data is None:
        flash_io("This game does not exists.", "danger")
    elif (match_data.first_player_id == current_user.id \
      or match_data.second_player_id == current_user.id) \
      and (match_data.second_player_id is not None) and (game_data.status == 1):
        game_state = json.loads(game_data.game)
        state = foxintheforest.get_state_from_game(game_state)
        if (match_data.first_player_id == current_user.id and state["current_player"] == 0) \
        or (match_data.second_player_id == current_user.id and state["current_player"] == 1):
            if req["play"][-1] in foxintheforest.COLORS and int(req["play"][:-1]) < 13:
                card_played = foxintheforest.decode_card(req["play"])
                game_state = foxintheforest.play(game_state, [player, card_played])
                state = foxintheforest.get_state_from_game(game_state)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game_data.status = 2
                game_data.game = json.dumps(game_state)
                db.session.commit()
        emit("game changed", json.dumps({}), room=game_id)
    else:
        flash_io("You are not a player in this game.", "danger")
