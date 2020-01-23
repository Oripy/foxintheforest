from flask import flash, render_template, url_for, request, jsonify, make_response, redirect
from foxy import app, db, bcrypt
from foxy.forms import RegistrationForm, LoginForm
from foxy.models import User, Games
from flask_login import login_user, logout_user, current_user, login_required
from uuid import uuid4
import foxy.foxintheforest as foxintheforest
import random

games = {}

def get_new_id():
    while True:
        new_id = uuid4()
        if not new_id in games: break
    return str(new_id)

@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

@app.route("/new", methods=["POST"])
def new():
    req = request.get_json()
    id = get_new_id()
    games[id] = foxintheforest.new_game(id)

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
    return render_template('lobby.html', games=games)

@app.route("/play", methods=["POST"])
@login_required
def play():
    req = request.get_json()
    card_played = None
    if req["play"] == "new_game":
        id = get_new_id()
        games[id] = foxintheforest.new_game(id)
    elif req["player"] == 1:
        id = req["id"]
        card_played = random.choice(foxintheforest.list_allowed(games[id], 1))
        games[id] = foxintheforest.play(games[id], (1, card_played))
    elif req["play"][-1] in ["h", "s", "c"] and int(req["play"][:-1]):
        id = req["id"]
        card_played = foxintheforest.decode_card(req["play"])
        print(card_played)
        games[id] = foxintheforest.play(games[id], (0, card_played))
    res = make_response(jsonify(games[id]), 200)
    return res