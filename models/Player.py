from enum import Enum
from abilities import ability

class Player:
    playername = ''
    abilities = []
    def __init__(self, name):
        self.playername = name
    def addAbility(self, ability):
        self.abilities.append(ability)
