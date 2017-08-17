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
        max_id = max(player.player_id for player in players) + 1
    pl = Player(nickname, max_id)
    players.append(pl)
    return pl

def getPlayerById(id): #returns None if user can't be found
    pl = next((p for p in players if p.player_id == id), None)
    return pl

def getRoomById(id): #returns None if room can't be found
    room = next((r for r in rooms if r.room_id == id), None)
    return room

def addUserToFreeRoom(user): #returns None if an error occurs in room organization
    max_room_id = 0
    if rooms:#if there are rooms, get the biggest one and find the id
        max_room_id = max(room.room_id for room in rooms)
        max_room = getRoomById(max_room_id)
        if max_room == None:
             return None
        if max_room.playerCount() < 2: #max room
            if(max_room.addPlayer(user) == None):
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
    if room.playerCount() == 2: #if room is ready
        room.getPlayer(1).addAbility(Ability.LEFT)
        room.getPlayer(1).addAbility(Ability.JUMP)
        room.getPlayer(2).addAbility(Ability.RIGHT)
        room.getPlayer(2).addAbility(Ability.DOUBLE_JUMP)
        room.getPlayer(2).addAbility(Ability.DROP)
    emit('player joined', ','.join(map(str, room.getPlayer(1).abilities)) + ' | ' + ','.join(map(str, room.getPlayer(2).abilities)), room=room_id)

@socketio.on('tryright')
def on_tryright(data):
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
def on_tryjump(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.JUMP):
        emit('move jump', None , room=room_id)

@socketio.on('trydoublejump')
def on_trydouble(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.DOUBLE_JUMP):
        emit('move double jump', None , room=room_id)

@socketio.on('trydrop')
def on_trydrop(data):
    room_id = data['room_id']
    player_id = data['player_id']
    player = getPlayerById(player_id)
    if player.hasAbility(Ability.DROP):
        emit('move drop', None , room=room_id)
#END NETWORK TRAFFIC
