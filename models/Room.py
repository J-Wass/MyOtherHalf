from Player import Player

class Room:
    room_id = -1
    player1 = Player('null', -1)
    player2 = Player('null', -1)
    level = -1
    player_count = 0
    def __init__(self, id):
        self.room_id = id
        self.player1 = Player('null', -1)
        self.player2 = Player('null', -1)
        self.level = -1
        self.player_count = 0
    #adds a new player to the room, returns None if the room is full
    def addPlayer(self, player):
        if self.player_count == 0:
            self.player1 = player
            self.player_count += 1
        elif self.player_count == 1:
            self.player2 = player
            self.player_count += 1
        else:
            return None
        return player
