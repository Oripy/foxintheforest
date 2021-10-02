from foxy.foxintheforest import list_allowed, get_state_from_game
from random import choice

def ai_play(game):
    state = get_state_from_game(game)
    return choice(list_allowed(state, 1))
