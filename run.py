"""Runs the Fox in the Forest Flask server"""
try:
    from gevent import monkey
except ModuleNotFoundError:
    print("gevent module not found. Must be using Flask dev server.")
    pass
else:
    monkey.patch_all()

from foxy import app, socketio

if __name__ ==  '__main__':
    socketio.run(app)
