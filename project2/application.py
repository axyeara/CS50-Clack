import os

from flask import Flask, render_template, request, jsonify, redirect
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


channels = {} #a dictionary where channel is key and value is a list of tuples of user, datetime and the message of the user
usernames = []

@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        username = request.get_json(force=True)["username"] #this finally works

        return username in usernames

@app.route("/users", methods=["GET"])
def users():
    if request.method == "GET":
        return jsonify({'users': usernames})

@app.route("/channels", methods=["GET"])
def getChannels():
    if request.method == "GET":
        return jsonify({'channels':list(channels.keys())})

@app.route("/messagesresult", methods=["POST"])
def getMessages():
    if request.method == "POST":
        channel = request.get_json(force=True)["channel"]
        return jsonify({'messages': channels[channel]})

@socketio.on("log user")
def logUser(data):
    username = data["username"]
    if username not in usernames:
        usernames.append(username)
    emit("add user", usernames, broadcast=True)


@socketio.on("logout user")
def logoutUser(data):
    username = data["username"]
    if username in usernames:
        usernames.remove(username)
    emit("remove user", usernames, broadcast=True)

@socketio.on("add message")
def addMessage(data):
    channel = data["channel"];
    username = data["username"];
    message = data["message"];
    timedate = str(datetime.now())[:19]
    if channel in channels:
        channels[channel].append((username, timedate, message))
        emit("add message", channel, broadcast=True)



# Adds new channel to the server dictionary with an empty list. Then emits
# to the rest of the clients so they can update their channel list too
@socketio.on("add channel")
def addChannel(data):
    channel = data["channel"]
    if channel not in channels:
        channels[channel] = []
        emit("new channel", list(channels.keys()), broadcast=True)
    else:
        emit("invalid channel", list(channels.keys()), broadcast=False)

if __name__ == "__main__":
    app.run(debug=True)
