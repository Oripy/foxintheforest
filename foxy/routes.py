from flask import flash, render_template, url_for, request, json, jsonify, make_response, redirect
from foxy import app, db, bcrypt
from foxy.forms import RegistrationForm, LoginForm
from foxy.models import User, Games
from flask_login import login_user, logout_user, current_user, login_required
import foxy.foxintheforest as foxintheforest
import foxy.random_ai as random_ai
import foxy.good_ai as good_ai

AI_dict = {"TheBad": random_ai, "TheGood": good_ai} 

@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

@app.route("/new", methods=['POST'])
@login_required
def new():
    game = foxintheforest.new_game()
    game = json.dumps(game)
    if 'AI' in request.form:
        ai = User.query.filter_by(username=request.form['AI']).first()
        if ai:
            game_db = Games(game=game, name=request.form['gamename'], first_player_id=current_user.id, second_player_id=ai.id, status=1)
        else:
            flash(f'This AI does not exists.', 'danger')
            return redirect(url_for('lobby'))
    else:
        game_db = Games(game=game, name=request.form['gamename'], first_player_id=current_user.id)
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
        gameState = json.loads(game.game)
        state = foxintheforest.get_state_from_game(gameState)
        if (game.first_player_id == current_user.id and state["current_player"] == 0) \
           or (game.second_player_id == current_user.id and state["current_player"] == 1):
            if req["play"][-1] in foxintheforest.COLORS and int(req["play"][:-1]) < 13:
                card_played = foxintheforest.decode_card(req["play"])
                gameState = foxintheforest.play(gameState, [player, card_played])
                state = foxintheforest.get_state_from_game(gameState)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game.status = 2
                game.game = json.dumps(gameState)
                db.session.commit()
        return make_response(jsonify(foxintheforest.get_player_game(gameState, player)), 200)
    else:
        flash(f'You are not a player in this game.', 'danger')
        return redirect(url_for('lobby'))

@app.route("/get_game", methods=["POST"])
@login_required
def get_game():
    req = request.get_json()
    game_id = req["id"]
    game = Games.query.filter_by(id=game_id).first()
    if game == None:
        flash(f'This game does not exists.', 'danger')
        return redirect(url_for('lobby'))
    if game.second_player:
        gameState = json.loads(game.game)
        if game.second_player.username in AI_dict.keys():
            state = foxintheforest.get_state_from_game(gameState)
            if state["current_player"] == 1:
                ai_play = AI_dict[game.second_player.username].ai_play(foxintheforest.get_player_game(gameState, 1))
                gameState = foxintheforest.play(gameState, ai_play)
                state = foxintheforest.get_state_from_game(gameState)
                if len(state["discards"][0]) + len(state["discards"][1]) == 26:
                    game.status = 2
                game.game = json.dumps(gameState)
                db.session.commit()
    if game.first_player_id == current_user.id:
        gameState = json.loads(game.game)
        return make_response(jsonify(foxintheforest.get_player_game(gameState, 0)), 200)
    elif game.second_player_id == current_user.id:
        gameState = json.loads(game.game)
        return make_response(jsonify(foxintheforest.get_player_game(gameState, 1)), 200)
    else:
        flash(f'You are not a player in this game.', 'danger')
        return redirect(url_for('lobby'))