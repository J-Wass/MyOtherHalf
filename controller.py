#handles URL routing, initialization of models, and socket traffic

from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, emit
from flask_socketio import join_room, leave_room
import os
import random
from models.abilities import ability
from models.Player import Player
from models.Room import  Room

#GLOBALS
app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
key = os.urandom(24)
app.config['SECRET_KEY'] = key
app.secret_key = key
socketio = SocketIO(app)

# list of Usernames in the game already
Usernames = ['mod', 'Mod', 'moderator', 'Moderator', 'admin', 'Admin', 'administrator', 'Administrator', 'LeChosenOne']
Rooms = []
#END GLOBALS

#MODEL METHODS
def CreateUser(nickname):
    Usernames.append(nickname)
    return Player(nickname)

def GetRoomById(id): #returns None if room can't be found
    room = next((r for r in Rooms if r.roomId == id), None)#get the first room with the id, or none
    return room

def FindOrCreateRoom(user): #returns None if an error occurs in room organization
    maxRoomId = 0
    if Rooms:#if there are rooms, get the biggest one and find the id
        maxRoomId = max(Room.roomId for Room in Rooms)
        print maxRoomId
        maxRoom = GetRoomById(maxRoomId)
        if(maxRoom == None): #if room couldn't be found, but its id is in the room listing
             return None
        if maxRoom.playerCount < 2: #joining max room
            if(maxRoom.AddPlayer(user) == None): #if room is full, but isn't supposed to be
                return None
            Rooms.append(maxRoom)
            return maxRoom
    newRoom = Room(maxRoomId + 1)#create the new largest room
    newRoom.AddPlayer(user)
    Rooms.append(newRoom)
    return newRoom
#END MODEL METHODS

#ROUTING METHODS
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.j2')


@app.route('/game', methods=['POST'])
def game():
    nickname = str(request.form['nickname'])
    if nickname in Usernames:
        return render_template('index.j2', error = "Nickname: '" + nickname + "' is already in use!")
    user = CreateUser(nickname)
    room = FindOrCreateRoom(user)
    if(user == None or room == None):
        return render_template('index.j2', error = "There was an error finding a room. Please try again later.")
    return render_template('game.j2', User = user, Room = room )
#END ROUTING METHODS

#HANDLE SOCKET TRAFFIC
@socketio.on('joinroom')
def on_joinroom(data):
    roomid = data['roomid']
    username = str(data['username'])
    join_room(roomid)
    print('player joined room: ' + str(username) + ' ' + str(roomid))
    emit('joinroom response', str(username) + ' ' + str(roomid), room=roomid)
#END SOCKET TRAFFIC
