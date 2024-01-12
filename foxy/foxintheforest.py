"""Implementation of Fox in the Forest, a trick-taking game for two players
designed by Joshua Buergel

The game state is fully described as:
    a dict with the following keys:
        plays: list of plays so far
        first_player: starting player
        init_draw_deck: starting draw deck (6 cards)
        init_trump_card: starting trump card
        init_hands: a list of the two starting hands
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Union, Any
import random
from copy import copy

Card = List[Union[int, str, None]]
Play = List[Union[int, Card]]
State = Dict[str, Any]
Game = Dict[str, Any]

COLORS: List[str] = ["h", "s", "c"]
CARDS: List[Card] = [[a, b] for b in COLORS for a in range(1, 12)]

def other_player(player: int) -> int:
    """Returns the opponent number"""
    return 1 - player

def pick_cards(deck: List[Card], num: int) -> List[Card]:
    """Return a number of cards from the top of the given list of cards"""
    cards: List[Card] = deck[:num]
    del deck[:num]
    return cards

def new_game() -> Game:
    """Create a new game"""
    draw_deck: List[Card] = copy(CARDS)
    random.shuffle(draw_deck)
    hands: List[List[Card]] = []
    for _ in range(2):
        hands.append(pick_cards(draw_deck, 13))
    trump_card: Card = pick_cards(draw_deck, 1)[0]
    first_player: int = random.randint(0, 1)
    return {
        "plays": [],
        "first_player": first_player,
        "init_draw_deck": draw_deck,
        "init_trump_card": trump_card,
        "init_hands": hands
    }

def copy_game(game: Game) -> Game:
    """Output a cloned copy of the given game """
    return {
        "plays": game["plays"].copy(),
        "first_player": game["first_player"],
        "init_draw_deck": game["init_draw_deck"].copy(),
        "init_trump_card": game["init_trump_card"],
        "init_hands": [game["init_hands"][0].copy(), game["init_hands"][1].copy()]
    }

def copy_state(state: State) -> State:
    """Output a cloned copy of the given state """
    return {
        "plays": state["plays"].copy(),
        "private_discards": [state["private_discards"][0].copy(),
                             state["private_discards"][1].copy()],
        "trick": [state["trick"][0],state["trick"][1]],
        "current_player": state["current_player"],
        "leading_player": state["leading_player"],
        "score": [state["score"][0], state["score"][1]],
        "discards": [state["discards"][0].copy(), state["discards"][1].copy()],
        "hands": [state["hands"][0].copy(), state["hands"][1].copy()],
        "init_trump_card": state["init_trump_card"],
        "trump_card": state["trump_card"],
        "draw_deck": state["draw_deck"].copy()
    }

def get_state_from_game(game: Game) -> State:
    """Returns the current status of a game state
        a state is a dict with the following keys:
            plays: list of plays so far
            private_discards: list of cards secretely discarded by each player
            trick: list of cards of the current trick played
            current_player: next player to play
            leading_player: player leading the current trick
            score: score ([0, 0] if the game is not yet finished)
            discards: list of cards won by each player
            hands: a list of the two hands
            init_trump_card: starting trump card, necessary to know to have
                a full knowledge of a game
            trump_card: current trump card
            draw_deck: cards remaining in the draw deck"""
    state: State = {}
    state["plays"] = []
    state["private_discards"] = [[], []]
    state["trick"] = [None, None]
    state["current_player"] = game["first_player"]
    state["leading_player"] = game["first_player"]
    state["score"] = [0, 0]
    state["discards"] = [[], []]
    state["hands"] = [game["init_hands"][0].copy(), game["init_hands"][1].copy()]
    state["init_trump_card"] = game["init_trump_card"]
    state["trump_card"] = game["init_trump_card"]
    state["draw_deck"] = game["init_draw_deck"].copy()
    special_type: Union[int, None] = None
    for step in game["plays"]:
        state, special_type = do_step(state, step, special_type)
    if len(state["hands"][0]) + len(state["hands"][1]) == 0:
        state["score"] = get_score(state)
    return state

def do_step(state: State, step: Play,
            special_type: Union[int, None]) -> Tuple[State, Union[int, None]]:
    """Apply a play to a State and returns the next State"""
    state["plays"].append(step)
    if special_type is None:
        state["trick"][step[0]] = step[1]
        if step[1] in state["hands"][step[0]]:
            state["hands"][step[0]].pop(state["hands"][step[0]].index(step[1]))
        else:
            state["hands"][step[0]].pop(0)
        if step[1][0] == 3:
            special_type = 3
            state["hands"][step[0]].append(state["trump_card"])
            state["trump_card"] = []
        elif step[1][0] == 5:
            special_type = 5
            state["hands"][step[0]].append(pick_cards(state["draw_deck"], 1)[0])
    elif special_type == 5:
        state["private_discards"][step[0]].append(step[1])
        if step[1] in state["hands"][step[0]]:
            state["hands"][step[0]].pop(state["hands"][step[0]].index(step[1]))
        else:
            state["hands"][step[0]].pop(0)
        special_type = None
    elif special_type == 3:
        state["trump_card"] = step[1]
        if step[1] in state["hands"][step[0]]:
            state["hands"][step[0]].pop(state["hands"][step[0]].index(step[1]))
        else:
            state["hands"][step[0]].pop(0)
        special_type = None
    if special_type is None:
        if not None in state["trick"]:
            win, state["leading_player"] = trick_winner(state["leading_player"],
                                                        state["trick"], state["trump_card"])
            state["discards"][win].append(state["trick"][0])
            state["discards"][win].append(state["trick"][1])
            state["trick"] = [None, None]
            state["current_player"] = state["leading_player"]
        else:
            state["current_player"] = other_player(step[0])
    return state, special_type

def get_player_game(game: Game, player: int) -> Game:
    """Returns a Game state stripped-off information that is not known by the player"""
    hands: List[List[Card]] = [[], []]
    hands[player] = game["init_hands"][player].copy()
    hands[other_player(player)] = [[None, None]] * len(game["init_hands"][other_player(player)])
    game_player: Game = {
        "player": player,
        "plays": [],
        "first_player": game["first_player"],
        "init_draw_deck": [],
        "init_trump_card": game["init_trump_card"],
        "init_hands": hands
    }
    picked: int = 0
    next_special: bool = False
    hide_next: bool = False
    for step in game["plays"]:
        if hide_next:
            game_player["plays"].append([step[0], [None, None]])
        else:
            game_player["plays"].append(step)
        if step[1][0] == 5 and not next_special:
            next_special = True
            if step[0] == player:
                game_player["init_draw_deck"].append(game["init_draw_deck"][picked])
                picked += 1
            else:
                hide_next = True
                game_player["init_draw_deck"].append([None, None])
                picked += 1
        elif step[1][0] == 3 and not next_special:
            next_special = True
        elif next_special:
            next_special = False
            hide_next = False
    game_player["init_draw_deck"] += [[None, None]]*(6-picked)
    return game_player

def play(game: Game, step: Play) -> Game:
    """Apply a play to a Game and returns the next Game"""
    state: State = get_state_from_game(game)
    if valid_step(state, step):
        game = apply_play(game, step)
    return game

def apply_play(game: Game, step: Play) -> Game:
    """Blindly apply a play to a Game and returns the next Game
        Warning: can return an invalid game state
            the validity of the play is not checked, use play() if check is necessary
    """
    game["plays"].append(step)
    return game

def trick_winner(leading_player: int, trick: List[Card],
                 trump_card: Card) -> Tuple[int, int]:
    """Returns the winner of a trick as well as the next leading player"""
    winner: int
    next_leading_player: int
    trump_suit: str = trump_card[1]
    card0_suit: str = trick[0][1]
    card0_value: int = trick[0][0]
    card1_suit: str = trick[1][1]
    card1_value: int = trick[1][0]

    # 9 change suit if not paired with an other 9
    if card0_value == 9:
        if card1_value != 9:
            card0_suit = trump_suit
    if card1_value == 9:
        if card0_value != 9:
            card1_suit = trump_suit

    if card0_suit == card1_suit: # Same suit
        if card0_value > card1_value:
            winner = 0
        else:
            winner = 1
    else: # different suit
        if card0_suit == trump_suit:
            winner = 0
        elif card1_suit == trump_suit:
            winner = 1
        else:
            winner = leading_player
    if winner == 0:
        if card1_value == 1:
            next_leading_player = 1
        else:
            next_leading_player = 0
    else:
        if card0_value == 1:
            next_leading_player = 0
        else:
            next_leading_player = 1
    return (winner, next_leading_player)

def valid_step(state: State, step: Play) -> bool:
    """Check if a play is valid"""
    player: int = step[0]
    card: Card = step[1]
    # print(card, player, state)
    # print(f"testing player {player}")
    if not player == state["current_player"]:
        # print(f"NOK, player {player} not supposed to play")
        return False
    # print(f"OK, player {player} turn to play")
    # print(f"testing {card}")
    if card in state["hands"][player]:
        # print("OK, card in hand")
        if state["trick"][player] is None:
            # print("OK, no card already played for this player")
            other_card = state["trick"][other_player(player)]
            if other_card is None:
                # print("OK first card played")
                return True
            else:
                if other_card[1] == card[1]: # Same suit
                    if other_card[0] == 11: # Force best card or 1
                        if card[0] == 1:
                            # print("OK, 11 forced 1 or best")
                            return True
                        else:
                            same_suit_list = []
                            for card_in_hand in state["hands"][player]:
                                if card_in_hand[1] == other_card[1]:
                                    same_suit_list.append(card_in_hand)
                            same_suit_list.sort(key=lambda a: a[0])
                            if card == same_suit_list[-1]:
                                # print("OK, 11 forced 1 or best")
                                return True
                            else:
                                # print("NOK, 11 is forcing 1 or best", card, same_suit_list)
                                return False
                    else:
                        # print("OK, same suit and nothing forcing")
                        return True
                else: # Different suit
                    same_suit_list = []
                    for card in state["hands"][player]:
                        if card[1] == other_card[1]:
                            same_suit_list.append(card)
                    if len(same_suit_list) == 0:
                        # print("OK, no card on the same suit available")
                        return True
                    else:
                        # print("NOK, play card of the same suit")
                        return False
        else:
            # print("Card already played for this player", state["trick"][player])
            if ((state["plays"][-1][1][0] == 3 or state["plays"][-1][1][0] == 5)
                 and state["plays"][-1][0] == player):
                return True
            else:
                return False
    else:
        # print("NOK, card not in hand")
        return False

def get_score(state: State) -> List[int]:
    """Get the score of a finished game"""
    score: List[int] = [0, 0]
    for player in range(2):
        for card in state["discards"][player]:
            if card[0] == 7:
                score[player] += 1

    tricks_won: List[int] = [len(state["discards"][0])//2, len(state["discards"][1])//2]

    if tricks_won[0] + tricks_won[1] == 13:
        for player in range(2):
            if tricks_won[player] <= 3: # Humble
                score[player] += 6
            elif tricks_won[player] == 4: # Defeated
                score[player] += 1
            elif tricks_won[player] == 5: # Defeated
                score[player] += 2
            elif tricks_won[player] == 6: # Defeated
                score[player] += 3
            elif tricks_won[player] <= 9: # Victorious
                score[player] += 6
            else: # Greedy
                score[player] += 0
    return score

def decode_card(card_text: str) -> Union[Card, bool]:
    """Return a card object using a text input"""
    try:
        return [int(card_text[:-1]), card_text[-1]]
    except ValueError:
        return False

def show(state: State, player: int) -> None:
    """Print the state of the game in the console"""
    if state["current_player"] == player:
        print("------------")
        print(f'Joueur {state["current_player"]}')
        if state["trump_card"]:
            print(f'[**] [{state["trump_card"][0]}{state["trump_card"][1]}]')
        else:
            print("[**] [xx]")
        print("Pli : J0 {} / J1 {}".format(*["[{}{}]".format(c[0], c[1])
            if c is not None else "[xx]" for c in [state["trick"][0], state["trick"][1]]]))
        print(" ".join(["[{}{}]".format(c[0], c[1])
            for c in sorted(state["hands"][player], key = lambda a: (a[1], a[0]), reverse = True)]))

def list_allowed(state: State, player: int) -> List[Play]:
    """Returns a list of allowed plays for the given player."""
    if state["current_player"] != player:
        return []

    if state["trick"][player] is not None:
        return [[player, card] for card in state["hands"][player]]

    if state["trick"][0] is None and state["trick"][1] is None:
        return [[player, card] for card in state["hands"][player]]

    allowed = []
    other_card = state["trick"][other_player(player)]

    best_card = None
    for card in state["hands"][player]:
        if other_card[1] == card[1]: # Same suit
            if other_card[0] == 11: # Force best card or 1
                if card[0] == 1:
                    allowed.append([player, card])
                else:
                    if not best_card:
                        best_card = card
                    elif card[0] > best_card[0]:
                        best_card = card
            else:
                allowed.append([player, card])
    if best_card:
        allowed.append([player, best_card])

    if len(allowed) == 0:
        allowed.append([player, card])
    return allowed

if __name__ ==  '__main__':
    game_test: Game = new_game()
    print(game_test)
    state_test: State = get_state_from_game(game_test)
    current_player: int
    while len(state_test["hands"][0]) != 0 or len(state_test["hands"][1]) != 0:
        current_player = state_test["current_player"]
        show(state_test, current_player)
        if current_player == 0:
            state_0 = get_state_from_game(get_player_game(game_test, 0))
            # print(state_0)
            # card_played = decode_card(input("Carte ? "))
            # selected_play = [0, card_played]
            selected_play = random.choice(list_allowed(state_0, 0))
        else:
            state_1 = get_state_from_game(get_player_game(game_test, 1))
            selected_play = random.choice(list_allowed(state_1, 1))
        print(f'Carte : {selected_play[1][0]}{selected_play[1][1]}')
        play(game_test, selected_play)
        state_test = get_state_from_game(game_test)

    print("Résultat :")
    print(f'Plis gagnés : P0 {len(state_test["discards"][0])//2}, '
          f'P1 {len(state_test["discards"][1])//2}'
    )
    print(f'Score : P0 {get_score(state_test)[0]}, P1 {get_score(state_test)[1]}')
