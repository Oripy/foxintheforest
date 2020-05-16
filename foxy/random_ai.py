from foxy.foxintheforest import list_allowed
from random import choice

def ia_play(state):
    return choice(list_allowed(state, 1))
