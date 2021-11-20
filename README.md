# Foxy

## About The Project

This is an implementation of [The Fox in the Forest, a trick-taking game for two players designed by Joshua Buergel](https://boardgamegeek.com/boardgame/221965/fox-forest).

I started building this because I wanted to toy around with building an Artificial Intelligence for a game, and because this is one of my favorite game.

I also used this project to learn about using python for web servers, using Flask.

## Built With

* [Python](https://www.python.org/) I used python 3.8
* [Flask](https://flask.palletsprojects.com)
* [SocketIO](https://socket.io/)
* [Javascript](https://developer.mozilla.org/fr/docs/Web/JavaScript)
* [CSS](https://developer.mozilla.org/fr/docs/Web/CSS)
* [HTML](https://developer.mozilla.org/fr/docs/Web/HTML)
* [Redis Queue](https://python-rq.org)

### Flask Extensions used

* [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com) to connect to the database storing users and games data
* [Flask Migrate](https://flask-migrate.readthedocs.io) to be able to upgrade the DB when structure changes
* [Flask Login](https://flask-login.readthedocs.io) to deal with user sessions
* [Flask BCrypt](https://flask-bcrypt.readthedocs.io/) to hash passwords, because no one wants its password stored in plain text
* [Flask SocketIO](https://flask-socketio.readthedocs.io) to have an easy time with SocketIO messages handling
* [Flask Babel](https://flask-babel.tkte.ch/) to translate the App
* [Flask WTF](https://flask-wtf.readthedocs.io) for forms

## Getting Started

Installing should be quite straightforward for someone used to Flask.

### Prerequisites

Create a new directory and clone the repo in it

```
mkdir foxy
cd foxy
git clone https://github.com/Oripy/foxintheforest.git
```

Create a new venv and activate it (to not pollute your python installation)

```
python -m venv .venv/
source .venv/bin/activate # Line to enter before any commands below
```

Install all required packages

```
python -m pip install -r requirements/prod.txt
```

Config file should look like this in ```instance/config.py```

```
DEBUG = False
SECRET_KEY = "your secret key"

SQLALCHEMY_DATABASE_URI = "sqlite:///database.db" # path to you Database
SQLALCHEMY_TRACK_MODIFICATIONS = False

SESSION_COOKIE_SAMESITE = "Strict"

LANGUAGES = ['en', 'fr']
```

### Running the program

Run the Redis server and start a worker with `rq worker`. 
Then use `python run.py`.

## Development

### Translation

Adding a new language ($LANG)

```
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel init -i messages.pot -d app/translations -l $LANG
```

Updating all languages (when new lines of text to translate have been added)

```
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d foxy/translations
```

Compile the translation files (when the tranlation files have been updated, or after a new installation)

```
pybabel compile -d foxy/translations
```

### Database

Migrate the database

```
export FLASK_APP=run.py
flask db upgrade
```

Update the migration files (after a change in db structure)

```
flask db migrate -m "Migration message."
```

## License

This software is distributed under the [GPLv3](LICENSE).