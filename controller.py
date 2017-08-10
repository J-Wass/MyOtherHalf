#handles URL routing, initialization of models, and socket traffic

from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, emit
from flask_socketio import join_room, leave_room
import os
import random
from models.Abilities import Ability
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
usernames = ['mod', 'Mod', 'moderator', 'Moderator', 'admin', 'Admin', 'administrator', 'Administrator', 'LeChosenOne']
players = []
rooms = []
#END GLOBALS

#MODEL METHODS
def createUser(nickname):
    usernames.append(nickname)
    max_id = 0
    if players:
        max_id = max(room.room_id for room in rooms) + 1
    pl = Player(nickname, max_id)
    players.append(pl)
    return pl

def getPlayerById(id):
    pl = next((p for p in players if p.player_id == id), None)#get the first player with the id, or none
    return pl

def getRoomById(id): #returns None if room can't be found
    room = next((r for r in rooms if r.room_id == id), None)#get the first room with the id, or none
    return room

def addUserToFreeRoom(user): #returns None if an error occurs in room organization
    max_room_id = 0
    if rooms:#if there are rooms, get the biggest one and find the id
        max_room_id = max(room.room_id for room in rooms)
        max_room = getRoomById(max_room_id)
        if max_room == None: #if room couldn't be found, but its id is in the room listing
             return None
        if max_room.player_count < 2: #joining max room
            if(max_room.addPlayer(user) == None): #if room is full, but isn't supposed to be
                return None
            rooms.append(max_room)
            return max_room
    new_room = Room(max_room_id + 1)#create the new largest room
    new_room.addPlayer(user)
    rooms.append(new_room)
    return new_room
#END MODEL METHODS

#ROUTING METHODS
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.j2')

@app.route('/game', methods=['POST'])
def game():
    nickname = str(request.form['nickname'])
    if nickname in usernames:
        return render_template('index.j2', error = "Nickname: '" + nickname + "' is already in use!")
    user = createUser(nickname)
    room = addUserToFreeRoom(user)
    if user == None or room == None:
        return render_template('index.j2', error = "There was an error finding a room. Please try again later.")
    return render_template('game.j2', User = user, Room = room )
#END ROUTING METHODS

#HANDLE NETWORK TRAFFIC
@socketio.on('joinroom')
def on_joinroom(data):
    room_id = data['room_id']
    player_id = data['player_id']
    join_room(room_id)

    #assign abilities
    room = getRoomById(room_id)
    if room.player_count == 2: #if room is ready
        room.player1.addAbility(Ability.LEFT)
        room.player1.addAbility(Ability.JUMP)
        room.player2.addAbility(Ability.RIGHT)
        room.player2.addAbility(Ability.DOUBLE_JUMP)
        room.player2.addAbility(Ability.DROP)
    emit('player joined', str(player_id) + ' ' + str(room_id), room=room_id)

@socketio.on('tryright')
def on_tryleft(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.RIGHT):
        emit('move right', None , room=room_id)

@socketio.on('tryleft')
def on_tryleft(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.LEFT):
        emit('move left', None , room=room_id)

@socketio.on('tryjump')
def on_tryleft(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.JUMP):
        emit('move jump', None , room=room_id)

@socketio.on('trydrop')
def on_tryleft(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.DROP):
        emit('move drop', None , room=room_id)
#END NETWORK TRAFFIC
