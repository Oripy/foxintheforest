"""Good AI for the Fox in the Forest game

This AI uses a Monte Carlo Tree Search algorithm adapted to hidden information
games inspired by Information Set Monte Carlo Tree Search (ISMCTS) algorithm
found in http://www.aifactory.co.uk/newsletter/2013_01_reduce_burden.htm

As there is no "standard" way of describing a game state in Fox in the Forest
this AI is heavily reliant on foxintheforest.py implementation.

Attributes:
    K (float): Parameter of the Upper Confidence Bound formula
    NB_SIMUL_P0 (int): Number of simulated games for each play

Point of entry is ai_play(game), the rest of methodes are private
"""
from __future__ import annotations

from typing import List, Dict, Union, Any
from random import shuffle
from math import sqrt, log

from foxy.foxintheforest import (
    copy_state, do_step, pick_cards, other_player, get_state_from_game, list_allowed, CARDS,
    Card, Play, State, Game
)

Knowledge = Dict[str, Any]

K: float = 5.0
"""Parameter of the Upper Confidence Bound formula"""

NB_SIMUL_P0: int = 5000
"""Number of simulated games for each play"""

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
        self.reward: int = 0
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
        return (f'{self.play} visits:{self.visits}'
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
        text += (f'{self.play} visits:{self.visits}'
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
                    opponent_cuts = []
                    opponent_hand = []
                    remaining_cards += draw_deck
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

def select(node: Node, state: State, ai_player: int) -> Node:
    """Select one of the allowed children based on UCT calculation """
    allowed: List[Play] = list_allowed(state, state["current_player"])
    list_children: List[Node] = []
    for play in allowed:
        exists: bool = False
        for child in node.children:
            if play[0] == child.play[0] and play[1] == child.play[1]:
                exists = True
                list_children.append(child)
                break
        if not exists:
            new_child = Node(play, node)
            node.add_child(new_child)
            list_children.append(new_child)

    min_max: float
    if ai_player == state["current_player"]:
        min_max = 0
    else:
        min_max = float("inf")

    selected: Node
    for child in list_children:
        child.availability += 1
    for child in list_children:
        if child.visits == 0:
            selected = child
            break
        value: float = upper_confidence_bound(child)
        if ai_player == state["current_player"]:
            if value > min_max:
                min_max = value
                selected = child
        else:
            if value < min_max:
                min_max = value
                selected = child
    return selected

def select_play(game: Game, runs: int) -> Union[Play, bool]:
    """Select one play based on MCTS simulations """
    state: State = get_state_from_game(game)
    allowed: List[Play] = list_allowed(state, state["current_player"])
    if len(allowed) == 0:
        return False
    if len(allowed) == 1:
        return allowed[0]

    root: Node = Node([-1, [-1, ""]])
    player: int = state["current_player"]
    knowledge: Knowledge = aquire_knowledge(state)
    for _ in range(runs):
        rand_state: State = random_state(state, knowledge)
        node: Node = root
        special_type: Union[int, None] = knowledge["special_type"]
        while len(rand_state["hands"][0]) != 0 or len(rand_state["hands"][1]) != 0:
            if node.visits < EXPANSION_THRESHOLD:
                rand_state, special_type = do_step(rand_state,
                    list_allowed(rand_state,
                                 rand_state["current_player"])[0],
                    special_type)
            else:
                node = select(node, rand_state, player)
                rand_state, special_type = do_step(rand_state, node.play, special_type)
        while node.parent is not None:
            node.visits += 1
            tricks_won: int = len(rand_state["discards"][0])//2
            if tricks_won <= 3:
                node.outcome_p0["humble"] += 1
                if player == 0:
                    node.reward += 1
            elif tricks_won <= 6:
                node.outcome_p0["defeated"] += 1
                if player == 1:
                    node.reward += 1
            elif tricks_won <= 9:
                node.outcome_p0["victorious"] += 1
                if player == 0:
                    node.reward += 1
            else:
                node.outcome_p0["greedy"] += 1
                if player == 1:
                    node.reward += 1
            node = node.parent
        root.visits += 1

    maxi:int = 0
    selected: Node
    for child in root.children:
        if child.visits > maxi:
            selected = child
            maxi = child.visits
    return selected.play

def ai_play(game: Game) -> Union[Play, bool]:
    """Select a play and return it"""
    return select_play(game, NB_SIMUL_P0)
