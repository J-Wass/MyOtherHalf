from enum import Enum
from Abilities import Ability

class Player:
    player_id = -1
    playername = ''
    abilities = []
    def __init__(self, name, new_id):
        self.abilities = []
        self.playername = name
        self.player_id = new_id
    def addAbility(self, ability):
        self.abilities.append(ability)
    def hasAbility(self, ability):
        return ability in self.abilities
