import random
from copy import copy
COLORS = ["h", "s", "c"]
CARDS = [[a, b] for b in COLORS for a in range(1, 12)]

def other_player(player):
    return 1 - player

def pick_cards(deck, num):
    cards = deck[:num]
    del deck[:num]
    return cards

def new_game():
    draw_deck = copy(CARDS)
    random.shuffle(draw_deck)
    hands = []
    for _ in range(2):
        hands.append(pick_cards(draw_deck, 13))
    trump_card = pick_cards(draw_deck, 1)[0]
    first_player = random.randint(0, 1)
    game = {
        "plays": [],
        "first_player": first_player,
        "init_draw_deck": draw_deck,
        "init_trump_card": trump_card,
        "init_hands": hands
    }    
    return game

def copy_game(game):
    """ output a cloned copy of the given game """
    return {
        "plays": game["plays"].copy(),
        "first_player": game["first_player"],
        "init_draw_deck": game["init_draw_deck"].copy(),
        "init_trump_card": game["init_trump_card"],
        "init_hands": [game["init_hands"][0].copy(), game["init_hands"][1].copy()]
    }

def copy_state(state):
    """ output a cloned copy of the given state """
    return {
        "plays": state["plays"].copy(),
        "private_discards": [state["private_discards"][0].copy(), state["private_discards"][1].copy()],
        "trick": [state["trick"][0],state["trick"][1]],
        "current_player": state["current_player"],
        "leading_player": state["leading_player"],
        "score": [state["score"][0], state["score"][1]],
        "discards": [state["discards"][0].copy(), state["discards"][1].copy()],
        "hands": [state["hands"][0].copy(), state["hands"][1].copy()],
        "trump_card": state["trump_card"],
        "draw_deck": state["draw_deck"].copy()
    }

def get_state_from_game(game):
    state = {}
    state["plays"] = []
    state["private_discards"] = [[], []]
    state["trick"] = [None, None]
    state["current_player"] = game["first_player"]
    state["leading_player"] = game["first_player"]
    state["score"] = [0, 0]
    state["discards"] = [[], []]
    state["hands"] = [game["init_hands"][0].copy(), game["init_hands"][1].copy()]
    state["trump_card"] = game["init_trump_card"]
    state["draw_deck"] = game["init_draw_deck"].copy()
    special_type = None
    for step in game["plays"]:
        state, special_type = do_step(state, step, special_type)
    if len(state["hands"][0]) + len(state["hands"][1]) == 0:
        state["score"] = score(state)
    return state

def do_step(state, step, special_type):
    state["plays"].append(step)
    if special_type == None:
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
    if special_type == None:
        if not None in state["trick"]:
            win, state["leading_player"] = trick_winner(state["leading_player"], state["trick"], state["trump_card"])
            state["discards"][win].append(state["trick"][0])
            state["discards"][win].append(state["trick"][1])
            state["trick"] = [None, None]
            state["current_player"] = state["leading_player"]
        else:
            state["current_player"] = other_player(step[0])
    return state, special_type

def get_player_game(game, player):
    hands = [[], []]
    hands[player] = game["init_hands"][player].copy()
    hands[other_player(player)] = [[None, None]] * len(game["init_hands"][other_player(player)])
    game_player = {
        "player": player,
        "plays": [],
        "first_player": game["first_player"],
        "init_draw_deck": [],
        "init_trump_card": game["init_trump_card"],
        "init_hands": hands
    }
    picked = 0
    next_special = False
    hide_next = False
    for p in game["plays"]:
        if hide_next:
            game_player["plays"].append([p[0], [None, None]])
        else:
            game_player["plays"].append(p)
        if p[1][0] == 5 and not next_special:
            next_special = True
            if p[0] == player:
                game_player["init_draw_deck"].append(game["init_draw_deck"][picked])
                picked += 1
            else:
                hide_next = True
                game_player["init_draw_deck"].append([None, None])
                picked += 1
        elif p[1][0] == 3 and not next_special:
            next_special = True
        elif next_special:
            next_special = False
            hide_next = False
    game_player["init_draw_deck"] += [[None, None]]*(6-picked)
    return game_player

def play(game, step):
    state = get_state_from_game(game)
    if valid_step(state, step):
        game = apply_play(game, step)
    return game

def apply_play(game, step):
    game["plays"].append(step)
    return game

def trick_winner(leading_player, trick, trump_card):
    # print("trick_winner", leading_player, trick, trump_card)
    if trick[0] == None or trick[1] == None:
        return False
    else:
        winner = None
        next_leading_player = None
        trump_suit = trump_card[1]
        card0_suit = trick[0][1]
        card0_value = trick[0][0]
        card1_suit = trick[1][1]
        card1_value = trick[1][0]

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
        # print("Winner:", trick, winner, next_leading_player)
        return (winner, next_leading_player)

def valid_step(state, step):
    player = step[0]
    card = step[1]
    # print(card, player, state)
    # print(f"testing player {player}")
    if not player == state["current_player"]:
        # print(f"NOK, player {player} not supposed to play")
        return False
    # else:
        # print(f"OK, player {player} turn to play")
    # print(f"testing {card}")
    if card in state["hands"][player]:
        # print("OK, card in hand")
        if state["trick"][player] == None:
            # print("OK, no card already played for this player")
            other_card = state["trick"][other_player(player)]
            if other_card == None:
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
                            for c in state["hands"][player]:
                                if c[1] == other_card[1]:
                                    same_suit_list.append(c)
                            same_suit_list.sort(key=lambda a: a[0])
                            if card == same_suit_list[-1]:
                                # print("OK, 11 forced 1 or best")
                                return True
                            else:
                                # print("NOK, 11 is forcing 1 or best", same_suit_list)
                                return False
                    else:
                        # print("OK, same suit and nothing forcing")
                        return True
                else: # Different suit
                    same_suit_list = []
                    for c in state["hands"][player]:
                        if c[1] == other_card[1]:
                            same_suit_list.append(c)
                    if len(same_suit_list) == 0:
                        # print("OK, no card on the same suit available")
                        return True
                    else:
                        # print("NOK, play card of the same suit")
                        return False
        else:
            # print("Card already played for this player", state["trick"][player])
            if (state["plays"][-1][1][0] == 3 or state["plays"][-1][1][0] == 5) and state["plays"][-1][0] == player:
                return True
            else:
                return False
    else:
        # print("NOK, card not in hand")
        return False

def score(state):
    score = [0, 0]
    for p in range(2):
        for c in state["discards"][p]:
            if c[0] == 7:
                score[p] += 1
    
    tricks_won = [len(state["discards"][0])//2, len(state["discards"][1])//2]

    if tricks_won[0] + tricks_won[1] == 13:
        for p in range(2):
            if tricks_won[p] <= 3: # Humble
                score[p] += 6
            elif tricks_won[p] == 4: # Defeated
                score[p] += 1 
            elif tricks_won[p] == 5: # Defeated
                score[p] += 2
            elif tricks_won[p] == 6: # Defeated
                score[p] += 3
            elif tricks_won[p] <= 9: # Victorious
                score[p] += 6
            else: # Greedy
                score[p] += 0
    return score

def decode_card(input):
    try:
        return [int(input[:-1]), input[-1]]
    except ValueError:
        return False

def show(state, player):
    if state["current_player"] == player:
        print("------------")
        print("Joueur {}".format(state["current_player"]))
        if state["trump_card"]:
            print("[**] [{}{}]".format(*state["trump_card"]))
        else:
            print("[**] [xx]")
        print("Pli : J0 {} / J1 {}".format(*["[{}{}]".format(c[0], c[1]) if c is not None else "[xx]" for c in [state["trick"][0], state["trick"][1]]]))
        print(" ".join(["[{}{}]".format(c[0], c[1]) for c in sorted(state["hands"][player], key = lambda a: (a[1], a[0]), reverse = True)]))

def list_allowed(state, player):
    if state["current_player"] == player:
        if state["trick"][player] != None:
            return [[player, card] for card in state["hands"][player]]
        elif state["trick"][0] == None and state["trick"][1] == None:
            return [[player, card] for card in state["hands"][player]]
        else:
            allowed = []
            other_card = state["trick"][other_player(player)]
            
            same_suit_list = []
            for card in state["hands"][player]:
                if card[1] == other_card[1]:
                    same_suit_list.append(card)
            same_suit_list.sort(key=lambda a: a[0])

            for card in state["hands"][player]:
                if other_card[1] == card[1]: # Same suit
                    if other_card[0] == 11: # Force best card or 1
                        if card[0] == 1:
                            # print("OK, 11 forced 1 or best")
                            allowed.append([player, card])
                        else:
                            if card == same_suit_list[-1]:
                                # print("OK, 11 forced 1 or best")
                                allowed.append([player, card])
                    else:
                        # print("OK, same suit and nothing forcing")
                        allowed.append([player, card])
                else: # Different suit
                    if len(same_suit_list) == 0:
                        # print("OK, no card on the same suit available")
                        allowed.append([player, card])
            return allowed
    else:
        return []

if __name__ ==  '__main__':
    game = new_game()
    print(game)
    state = get_state_from_game(game)
    while len(state["hands"][0]) != 0 or len(state["hands"][1]) != 0:
        current_player = state["current_player"]
        show(state, current_player)
        if current_player == 0:
            state_0 = get_state_from_game(get_player_game(game, 0))
            # print(state_0)
            # card_played = decode_card(input("Carte ? "))
            # selected_play = [0, card_played]
            selected_play = random.choice(list_allowed(state_0, 0))
        else:
            state_1 = get_state_from_game(get_player_game(game, 1))
            selected_play = random.choice(list_allowed(state_1, 1))
        print("Carte : {}{}".format(*selected_play[1]))
        play(game, selected_play)
        state = get_state_from_game(game)

    print("Résultat :")
    print("Plis gagnés : P0 {}, P1 {}".format(len(state["discards"][0])//2, len(state["discards"][1])//2))
    print("Score : P0 {}, P1 {}".format(*score(state)))