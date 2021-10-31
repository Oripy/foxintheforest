"""Dummy "AI" for the Fox in the Forest game

This AI only returns a random allowed play
"""
from __future__ import annotations
from typing import List, Union
from random import choice

from foxy.foxintheforest import list_allowed, get_state_from_game, State, Game, Play

def ai_play(game: Game) -> Union[Play, bool]:
    """Select a random allowed play and returns it"""
    state: State = get_state_from_game(game)
    allowed: List[Play] = list_allowed(state, 1)
    if len(allowed) == 0:
        return False
    return choice(allowed)
