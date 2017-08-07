from flask import Flask, session, render_template, request
from models.abilities import ability
from models.Player import Player
from models.Room import Room
import os
import random

# load app, set a secret key for sessions
app = Flask(__name__)
app.config['DEBUG'] = True
app.debug = True
app.secret_key = os.urandom(24)

# list of Usernames in the game room
Usernames = ['mod', 'Mod', 'moderator', 'Moderator', 'admin', 'Admin', 'administrator', 'Administrator', 'LeChosenOne']
Rooms = []

#model methods
def CreateUser(nickname):
    Usernames.append(nickname)
    return Player(nickname)

#returns None if room can't be found
def GetRoomById(id):
    room = next((r for r in Rooms if r.roomId == id), None)#get the first room with the id, or none
    return room

def FindOrCreateRoom(user):
    maxRoomId = 0
    if Rooms:#if there are rooms, get the biggest one and find the id
        maxRoomId = max(Room.roomId for Room in Rooms)
        print maxRoomId
        maxRoom = GetRoomById(maxRoomId)
        if(maxRoom == None): #if room couldn't be found
             return None
        if maxRoom.playerCount < 2: #joining max room
            if(maxRoom.AddPlayer(user) == None): #if room is full
                return None
            Rooms.append(maxRoom)
            return maxRoom
    newRoom = Room(maxRoomId + 1)#create the new largest room
    newRoom.AddPlayer(user)
    Rooms.append(newRoom)
    return newRoom

#routing methods
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
