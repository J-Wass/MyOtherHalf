from Player import Player

class Room:
    roomId = -1
    player1 = Player('null')
    player2 = Player('null')
    level = -1
    playerCount = 0
    def __init__(self, id):
        self.roomId = id
    #adds a new player to the room, returns None if the room is full
    def AddPlayer(self, player):
        if self.playerCount == 0:
            self.player1 = player
            self.playerCount += 1
        elif self.playerCount == 1:
            self.player2 = player
            self.playerCount += 1
        else:
            return None
        return player
