"""Runs the Fox in the Forest Flask server"""
from foxy import app, socketio

if __name__ ==  '__main__':
    socketio.run(app)
