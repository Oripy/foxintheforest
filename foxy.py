from flask import Flask, render_template, url_for, request, jsonify, make_response
from uuid import uuid4
import foxintheforest
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

games = {}

def get_new_id():
    while True:
        new_id = uuid4()
        if not new_id in games: break
    return new_id

@app.route("/")
def main():
    return render_template('game.html')

@app.route("/play", methods=["POST"])
def play():
    req = request.get_json()
    print(games)
    card_played = None
    if req["play"] == "new_game":
        id = str(get_new_id())
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

if __name__ ==  '__main__':
    app.run(debug=True)