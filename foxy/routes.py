from flask import flash, render_template, url_for, request, json, redirect
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import disconnect, emit

from foxy import app, db, bcrypt, socketio
from foxy.forms import RegistrationForm, LoginForm
from foxy.models import User, Games
from foxy import foxintheforest
from foxy import random_ai
from foxy import good_ai

AI_dict = {"TheBad": random_ai, "TheGood": good_ai}

def authenticated_only(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
            return None
        return f(*args, **kwargs)
    return wrapper

def flash_io(text, category):
    emit('message', json.dumps({"text": text, "category": category}))

@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

@app.route("/new", methods=['POST'])
@login_required
def new():
    game_state = json.dumps(foxintheforest.new_game())
    if 'AI' in request.form:
        ai = User.query.filter_by(username=request.form['AI']).first()
        if ai:
            game_db = Games(game=game_state, name=request.form['gamename'], 
                            first_player_id=current_user.id,
                            second_player_id=ai.id, status=1)
        else:
            flash('This AI does not exists.', 'danger')
            return redirect(url_for('lobby'))
    else:
        game_db = Games(game=game_state, name=request.form['gamename'], 
                        first_player_id=current_user.id)
    db.session.add(game_db)
    db.session.commit()
    return redirect(url_for('game', id=game_db.id))

@app.route("/game")
@login_required
def game():
    id = request.args.get("id")
    game_state = Games.query.filter_by(id=id).first()
    if game_state is None:
        flash(f'This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if game_state.first_player_id == current_user.id:
        return render_template('game.html', id=id,
            opponent=game_state.second_player.username
            if game_state.second_player is not None else None)
    if game_state.second_player_id == current_user.id:
        return render_template('game.html', id=id, opponent=game_state.first_player.username)
    if game_state.second_player_id is None:
        game_state.second_player_id = current_user.id
        game_state.status = 1
        db.session.commit()
        return render_template('game.html', id=id, opponent=game_state.first_player.username)
    flash('You are not a player in this game.', 'danger')
    return redirect(url_for('lobby'))

@app.route("/register", methods=['GET', 'POST'])
def register():
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
    logout_user()
    return redirect(url_for('main'))

@app.route("/lobby")
@login_required
def lobby():
    open_games = Games.query.filter((((Games.first_player_id==None)|(Games.second_player_id==None))&(Games.status<2)))
    own_games = Games.query.filter((((Games.first_player_id==current_user.id)|(Games.second_player_id==current_user.id))&(Games.status<2)))
    return render_template('lobby.html', open_games=open_games, own_games=own_games)

@socketio.on('play')
@authenticated_only
def play(data):
    req = json.loads(data)
    card_played = None
    game_id = req["id"]
    player = req["player"]
    game_data = Games.query.filter_by(id=game_id).first()
    if game_data is None:
        flash_io("This game does not exists.", "danger")
    elif (game_data.first_player_id == current_user.id \
      or game_data.second_player_id == current_user.id) \
      and (game_data.second_player_id is not None) and (game_data.status == 1):
        game_state = json.loads(game_data.game)
        state = foxintheforest.get_state_from_game(game_state)
        if (game_data.first_player_id == current_user.id and state["current_player"] == 0) \
        or (game_data.second_player_id == current_user.id and state["current_player"] == 1):
            if req["play"][-1] in foxintheforest.COLORS and int(req["play"][:-1]) < 13:
                card_played = foxintheforest.decode_card(req["play"])
                game_state = foxintheforest.play(game_state, [player, card_played])
                state = foxintheforest.get_state_from_game(game_state)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game_data.status = 2
                game_data.game = json.dumps(game_state)
                db.session.commit()
        emit("game state", json.dumps(foxintheforest.get_player_game(game_state, player)))
        if game_data.second_player.username in AI_dict.keys():
            state = foxintheforest.get_state_from_game(game_state)
            while state["current_player"] == 1 and game_data.status != 2:
                ai_play = AI_dict[game_data.second_player.username].ai_play(
                    foxintheforest.get_player_game(game_state, 1))
                game_state = foxintheforest.play(game_state, ai_play)
                state = foxintheforest.get_state_from_game(game_state)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game_data.status = 2
                game_data.game = json.dumps(game_state)
                db.session.commit()
                emit("game state", json.dumps(foxintheforest.get_player_game(game_state, player)))
    else:
        flash_io("You are not a player in this game.", "danger")

@socketio.on('get game')
@authenticated_only
def get_game(data):
    req = json.loads(data)
    game_id = req["id"]
    game_data = Games.query.filter_by(id=game_id).first()
    if game_data is None:
        flash_io('This game does not exists.', 'danger')
    elif game_data.status == 2:
        flash_io('Game finished.', 'danger')
    # if game.second_player:
    #     gameState = json.loads(game.game)
    elif game_data.first_player_id == current_user.id:
        game_state = json.loads(game_data.game)
        emit("game", json.dumps(foxintheforest.get_player_game(game_state, 0)))
    elif game_data.second_player_id == current_user.id:
        game_state = json.loads(game_data.game)
        emit("game", json.dumps(foxintheforest.get_player_game(game_state, 1)))
    else:
        flash_io('You are not a player in this game.', 'danger')
