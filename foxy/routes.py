from flask import flash, render_template, url_for, request, json, jsonify, make_response, redirect
from foxy import app, db, bcrypt
from foxy.forms import RegistrationForm, LoginForm
from foxy.models import User, Games
from flask_login import login_user, logout_user, current_user, login_required
import foxy.foxintheforest as foxintheforest
import foxy.random_ai as random_ai
import random

@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

@app.route("/new", methods=['POST'])
@login_required
def new():
    game = foxintheforest.new_game()
    state = json.dumps(game)
    if request.form['IA']:
        ia = User.query.filter_by(username=request.form['IA']).first()
        if ia:
            game_db = Games(state=state, name=request.form['gamename'], first_player_id=current_user.id, second_player_id=ia.id, status=1)
        else:
            flash(f'This IA does not exists.', 'danger')
            return redirect(url_for('lobby'))
    else:
        game_db = Games(state=state, name=request.form['gamename'], first_player_id=current_user.id)
    db.session.add(game_db)
    db.session.commit()
    return redirect(url_for('game', id=game_db.id))

@app.route("/game")
@login_required
def game():
    id = request.args.get("id")
    game = Games.query.filter_by(id=id).first()
    if game == None:
        flash(f'This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if game.first_player_id == current_user.id:
        return render_template('game.html', id=id, opponent=game.second_player.username if game.second_player != None else None)
    elif game.second_player_id == current_user.id:
        return render_template('game.html', id=id, opponent=game.first_player.username)
    elif game.second_player_id == None:
        game.second_player_id = current_user.id
        game.status = 1
        db.session.commit()
        return render_template('game.html', id=id, opponent=game.first_player.username)
    else:
        flash(f'You are not a player in this game.', 'danger')
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
        else:
            flash(f'Login unsuccessful. Please check username and password.', 'danger')
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

@app.route("/play", methods=["POST"])
@login_required
def play():
    req = request.get_json()
    card_played = None
    game_id = req["id"]
    player = req["player"]
    game = Games.query.filter_by(id=game_id).first()
    if game == None:
        flash(f'This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if (game.first_player_id == current_user.id or game.second_player_id == current_user.id) \
        and (game.second_player_id != None) and (game.status == 1):
        state = json.loads(game.state)
        if (game.first_player_id == current_user.id and state["current_player"] == 0) \
           or (game.second_player_id == current_user.id and state["current_player"] == 1):
            if req["play"][-1] in ["h", "s", "c"] and int(req["play"][:-1]):
                card_played = foxintheforest.decode_card(req["play"])
                state = foxintheforest.play(state, [player, card_played])
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game.status = 2
                game.state = json.dumps(state)
                db.session.commit()
        return make_response(jsonify(foxintheforest.get_player_state(state, player)), 200)
    else:
        flash(f'You are not a player in this game.', 'danger')
        return redirect(url_for('lobby'))

@app.route("/state", methods=["POST"])
@login_required
def state():
    req = request.get_json()
    game_id = req["id"]
    game = Games.query.filter_by(id=game_id).first()
    if game == None:
        flash(f'This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if game.second_player.username == "TheBad":
        state = json.loads(game.state)
        if state["current_player"] == 1:
            state = foxintheforest.play(state, [1, random_ai.ia_play(state)])
            if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                game.status = 2
            game.state = json.dumps(state)
            db.session.commit()
    if game.first_player_id == current_user.id:
        state = json.loads(game.state)
        return make_response(jsonify(foxintheforest.get_player_state(state, 0)), 200)
    elif game.second_player_id == current_user.id:
        state = json.loads(game.state)
        return make_response(jsonify(foxintheforest.get_player_state(state, 1)), 200)
    else:
        flash(f'You are not a player in this game.', 'danger')
        return redirect(url_for('lobby'))