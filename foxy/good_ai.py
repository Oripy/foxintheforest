"""Good AI for the Fox in the Forest game

This AI uses a Monte Carlo Tree Search algorithm adapted to hidden information
games inspired by Information Set Monte Carlo Tree Search (ISMCTS) algorithm
found in http://www.aifactory.co.uk/newsletter/2013_01_reduce_burden.htm

As there is no "standard" way of describing a game state in Fox in the Forest
this AI is heavily reliant on foxintheforest.py implementation.

Point of entry is ai_play(game), the rest of methodes are private
"""
from __future__ import annotations

from typing import List, Dict, Union, Any
from random import shuffle, choice
from math import sqrt, log, exp

from foxy.foxintheforest import (
    copy_state, do_step, pick_cards, other_player, get_state_from_game, list_allowed, CARDS,
    Card, Play, State, Game, get_score
)

from time import time, sleep

Knowledge = Dict[str, Any]

K: float = 1.4
"""Parameter of the Upper Confidence Bound formula"""

TURN_DURATION: int = 5
"""Time to think on each turn (seconds)"""

NB_SIMUL_P0: int = 1000
"""Number of simulated games for each batch before checking for time"""

EXPANSION_THRESHOLD: int = 1
"""Number of visits (and thus simulations) before expanding the node"""

class Node():
    """The Node object is one node of the Monte Carlo tree
    Args:
        play (list): this list describe the play that lead to this node
            [player, [card_value, card_suit]]
        parent (Node): the parent of this node (default: None for the root of the tree)

    Attributes:
        play (list): this list describe the play that lead to this node
            [player, [card_value, card_suit]]
        parent (Node): the parent of this node (default: None for the root of the tree)
        availability: number of time this node was a possible move to play
        visits: number of time this node was visited during the search
        reward: total reward received by this node
        children: list of children nodes
    """

    def __init__(self, play: Play, parent: Union[Node, None]=None) -> None:
        self.play: Play = play
        self.parent: Union[Node, None] = parent
        self.availability: int = 0
        self.visits: int = 0
        self.reward: float = 0
        self.children: List[Node] = []
        self.outcome_p0: Dict[str, int] = {"humble": 0, "defeated": 0,
                           "victorious": 0, "greedy": 0}

    def add_child(self, node: Node) -> None:
        """Add given child to the node children list."""
        self.children.append(node)

    def __repr__(self) -> str:
        denominator: int = (self.outcome_p0["humble"] + self.outcome_p0["defeated"] +
            self.outcome_p0["victorious"] + self.outcome_p0["greedy"]
        )
        if denominator == 0:
            denominator = 1
        return (f'{self.play} visits:{self.visits} '
            f'reward:{self.reward} av.:{self.availability} '
            f'h:{self.outcome_p0["humble"]/denominator*100:.2f}%,'
            f'd:{self.outcome_p0["defeated"]/denominator*100:.2f}%,'
            f'v:{self.outcome_p0["victorious"]/denominator*100:.2f}%,'
            f'g:{self.outcome_p0["greedy"]/denominator*100:.2f}% : '
            f'V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/denominator*100:.2f}'
        )

    def show(self, indent: int = 0, depth: int = 1) -> None:
        """Print the tree in the console starting at this node with the given depth """
        text: str = "  "*indent
        denominator: int = (self.outcome_p0["humble"] + self.outcome_p0["defeated"] +
            self.outcome_p0["victorious"] + self.outcome_p0["greedy"]
        )
        if denominator == 0:
            denominator = 1
        text += (f'{self.play} visits:{self.visits} '
            f'reward:{self.reward} av.:{self.availability} '
            f'h:{self.outcome_p0["humble"]/denominator*100:.2f}%,'
            f'd:{self.outcome_p0["defeated"]/denominator*100:.2f}%,'
            f'v:{self.outcome_p0["victorious"]/denominator*100:.2f}%,'
            f'g:{self.outcome_p0["greedy"]/denominator*100:.2f}% : '
            f'V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/denominator*100:.2f}'
        )
        print(text)
        if depth > 0:
            for node in sorted(self.children, key=lambda a: a.visits, reverse=True):
                node.show(indent=indent+1, depth=depth-1)

    def graph(self, depth: int = 1) -> str:
        """Outputs a Graphviz DOT language representation of the tree """
        denom: int = (self.outcome_p0["humble"] + self.outcome_p0["defeated"] +
            self.outcome_p0["victorious"] + self.outcome_p0["greedy"]
        )
        if denom == 0:
            denom = 1
        text: str = ""
        if self.play and isinstance(self.play[1], list):
            text += (f'{id(self)} [label="{self.play[0]}:{self.play[1][0]}{self.play[1][1]}'
                f'V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/denom*100:.2f}"];\n'
            )
        else:
            text += (f'{id(self)} [label="root'
                f'V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/denom*100:.2f}"];\n'
            )
        for node in self.children:
            text += f"{id(self)} -- {id(node)};\n"
        if depth > 0:
            for node in sorted(self.children, key=lambda a: a.visits, reverse=True):
                text += node.graph(depth=depth-1)
        return text

def upper_confidence_bound(node: Node) -> float:
    """Output Upper Confidence Bound formula result for the given node """
    return node.reward / node.visits + K * sqrt(log(node.availability) / node.visits)

def logistic(x: float) -> float:
    """Apply the logistic function to the input """
    return 1/(1+exp(-x))

def aquire_knowledge(state: State) -> Knowledge:
    """Extract knowledge on current state from past plays """
    remaining_cards: List[Card] = [c for c in CARDS
                        if c not in state["hands"][state["current_player"]]
                        if c not in state["discards"][0]
                        if c not in state["discards"][1]
                        if c not in state["private_discards"][state["current_player"]]
                        if c != state["trump_card"]
    ]
    draw_deck: List[Card] = []
    opponent_hand: List[Card] = []
    opponent_cuts: List[str] = []
    opponent_max_one: List[str] = []

    trump_card: Card = state['init_trump_card']
    trick: List[Card] = []
    next_special: Union[int, bool] = False
    for play in state["plays"]:
        if play[0] == other_player(state["current_player"]) and play[1] in opponent_hand:
            opponent_hand.remove(play[1])
        elif play[0] == other_player(state["current_player"]) and play[1][1] in opponent_max_one:
            opponent_max_one.remove(play[1][1])
            opponent_cuts.append(play[1][1])
        elif play[1] in remaining_cards:
            remaining_cards.remove(play[1])
        if next_special:
            if next_special == 3:
                trump_card = play[1]
            next_special = False
        else:
            if len(trick) == 2:
                trick = []
            if len(trick) == 0:
                trick.append(play)
            elif len(trick) == 1:
                trick.append(play)
                if trick[0][0] == state["current_player"]:
                    suit = trick[0][1][1]
                    if trick[1][1][1] != suit:
                        if suit not in opponent_cuts:
                            opponent_cuts.append(suit)
                        if suit in opponent_max_one:
                            opponent_max_one.remove(suit)
                    elif trick[0][1][0] == 11:
                        if (trick[1][1][0] != 1) and (trick[1][1][0] != 10):
                            for num in range(10, trick[1][1][0], -1):
                                if [num, suit] in remaining_cards:
                                    draw_deck.append([num, suit])
                                    remaining_cards.remove([num, suit])
            if play[1][0] == 5:
                if play[0] == other_player(state["current_player"]):
                    for cut in opponent_cuts:
                        if cut not in opponent_max_one:
                            opponent_max_one.append(cut)
                        else:
                            opponent_max_one.remove(cut)
                    remaining_cards += draw_deck
                    remaining_cards += opponent_hand
                    opponent_cuts = []
                    opponent_hand = []
                    draw_deck = []
                next_special = 5
            if play[1][0] == 3:
                if play[0] == other_player(state["current_player"]):
                    opponent_hand.append(trump_card)
                next_special = 3
    remaining_cards = [c for c in remaining_cards if c not in draw_deck]
    for cut in opponent_cuts:
        draw_deck += [c for c in remaining_cards if c[1] == cut]
        remaining_cards = [c for c in remaining_cards if c[1] != cut]

    special_type = None
    if next_special:
        special_type = state["plays"][-1][1][0]

    return {
        "remaining_cards": remaining_cards,
        "draw_deck": draw_deck,
        "opponent_hand": opponent_hand,
        "opponent_max_one": opponent_max_one,
        "special_type": special_type
    }

def random_state(state: State, knowledge: Knowledge) -> State:
    """Output a possible random state with the given knowledge """
    rand_state: State = copy_state(state)
    remaining_cards: List[Card] = list(knowledge["remaining_cards"])
    draw_deck: List[Card] = list(knowledge["draw_deck"])
    opponent_hand: List[Card] = list(knowledge["opponent_hand"])
    opponent_max_one: List[str] = list(knowledge["opponent_max_one"])
    shuffle(remaining_cards)
    nbr_unknown_cards_opp_hand: int = len(
        rand_state["hands"][other_player(rand_state["current_player"])]) - len(opponent_hand)
    for _ in range(nbr_unknown_cards_opp_hand):
        opponent_hand += pick_cards(remaining_cards, 1)
        if opponent_hand[-1][1] in opponent_max_one:
            opponent_max_one.remove(opponent_hand[-1][1])
            draw_deck += [c for c in remaining_cards if c[1]
                          == opponent_hand[-1][1]]
            remaining_cards = [c for c in remaining_cards if c[1] != opponent_hand[-1][1]]
    rand_state["hands"][other_player(rand_state["current_player"])] = opponent_hand
    rand_state["private_discards"][other_player(rand_state["current_player"])] = pick_cards(
        remaining_cards,
        len(rand_state["private_discards"][other_player(rand_state["current_player"])])
    )
    rand_state["draw_deck"] = draw_deck + remaining_cards
    return rand_state

def select(node: Node, state: State) -> Node:
    """Select one of the allowed children based on UCT calculation """
    allowed: List[Play] = list_allowed(state, state["current_player"])
    list_children: List[Node] = []
    for play in allowed:
        exists: bool = False
        for child in node.children:
            if play == child.play:
                exists = True
                child.availability += 1
                list_children.append(child)
                break
        if not exists:
            new_child = Node(play, node)
            new_child.availability += 1
            node.add_child(new_child)
            list_children.append(new_child)
    min_max: float = 0
    selected: Node
    for child in list_children:
        if child.visits == 0:
            return child
        value: float = upper_confidence_bound(child)
        if value > min_max:
            min_max = value
            selected = child
    return selected

def select_play(game: Game, duration: float, runs: int) -> Union[Play, bool]:
    """Select one play based on MCTS simulations """
    state: State = get_state_from_game(game)
    allowed: List[Play] = list_allowed(state, state["current_player"])
    max_running_time = duration*2
    if len(allowed) == 0:
        return False
    if len(allowed) == 1:
        sleep(duration)
        return allowed[0]

    root: Node = Node([-1, [-1, ""]])
    player: int = state["current_player"]
    knowledge: Knowledge = aquire_knowledge(state)
    start_time = time()
    selected: Node
    while True:
        for _ in range(runs):
            rand_state: State = random_state(state, knowledge)
            node: Node = root
            special_type: Union[int, None] = knowledge["special_type"]
            while len(rand_state["hands"][0]) != 0 or len(rand_state["hands"][1]) != 0:
                if node.visits < EXPANSION_THRESHOLD:
                    rand_state, special_type = do_step(rand_state,
                        choice(list_allowed(rand_state,
                                    rand_state["current_player"])),
                        special_type)
                else:
                    node = select(node, rand_state)
                    rand_state, special_type = do_step(rand_state, node.play, special_type)
            scores = get_score(rand_state)
            score_diff = scores[player] - scores[other_player(player)]
            reward: float = logistic(score_diff)
            while node.parent is not None:
                node.visits += 1
                if node.play[0] == player:
                    node.reward += reward
                else:
                    node.reward += 1 - reward
                node = node.parent
            root.visits += 1
        if (time() - start_time) > duration:
            selected = max(root.children, key=lambda x:x.reward/x.visits)
            if selected.play[1] == max(root.children, key=lambda x:x.visits).play[1]: # Checks if most visited is also the best reward
                break
            else:
                if (time() - start_time > max_running_time):
                    break
                duration *= 1.1
    return selected.play

def ai_play(game: Game, duration: float=TURN_DURATION, runs: int=NB_SIMUL_P0) -> Union[Play, bool]:
    """Select a play and return it"""
    return select_play(game, duration, runs)
