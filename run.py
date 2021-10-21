from foxy import app, socketio

if __name__ ==  '__main__':
    # app.run(debug=app.config["DEBUG"])
    socketio.run(app)