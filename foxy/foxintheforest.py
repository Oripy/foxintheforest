import random
from copy import copy, deepcopy
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
    for p in range(2):
        hands.append(pick_cards(draw_deck, 13))
    trump_card = pick_cards(draw_deck, 1)[0]
    first_player = random.randint(0, 1)
    state = {
        "plays": [],
        "leading_player": first_player,
        "current_player": first_player,
        "draw_deck": draw_deck,
        "trump_card": trump_card,
        "trick": [None, None],
        "hands": hands,
        "discards": [[], []],
        "private_discards": [[], []],
        "score": [0, 0]
    }    
    return state

def play(state, step):
    if valid_step(state, step):
        apply_play(state, step)
    return state

def apply_play(state, step):
    state["plays"].append(step)

    player = step[0]
    card = step[1]
    action = False

    state["hands"][player].remove(card)
    if state["trick"][player] != None :
        if state["trick"][player][0] == 5:
            state["private_discards"][player].append(card)
        elif state["trick"][player][0] == 3:
            state["trump_card"] = card
        state["current_player"] = other_player(player)
    else:
        state["trick"][player] = card
        state["current_player"] = other_player(player)

        if card[0] == 5 and len(state["hands"][player]) != 0:
            action = True
            card_draw = pick_cards(state["draw_deck"], 1)[0]
            state["hands"][player].append(card_draw)
            state["plays"][-1].append(card_draw)
            state["current_player"] = player
        elif card[0] == 3 and len(state["hands"][player]) != 0:
            action = True
            card_picked = state["trump_card"]
            state["hands"][player].append(card_picked)
            state["plays"][-1].append(card_picked)
            state["trump_card"] = None
            state["current_player"] = player

    if not action:
        if state["trick"][0] != None and state["trick"][1] != None:
            winner, leading_player = trick_winner(state["leading_player"], state["trick"], state["trump_card"])
            state["discards"][winner].append(state["trick"][winner])
            state["discards"][winner].append(state["trick"][other_player(winner)])
            state["trick"] = [None, None]
            state["leading_player"] = leading_player
            state["current_player"] = leading_player
    if len(state["hands"][0]) == 0 and len(state["hands"][1]) == 0:
        state["score"] = score(state)
    return state

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
    # print(f"testing {card}")
    if card in state["hands"][player]:
        # print("card in hand")
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
    # print(player_state, next_action)
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

def get_player_state(state, player):
    clean_plays = []
    change_next = False
    for p in state["plays"]:
        if change_next:
            clean_plays.append([p[0], [None, None]])
            change_next = False
        else:
            clean_plays.append(p)
            if p[0] == other_player(player) and p[1][0] == 5:
                change_next = True
    return {
        "plays": clean_plays,
        "player": player,
        "leading_player": state["leading_player"],
        "current_player": state["current_player"],
        "trump_card": state["trump_card"],
        "trick": state["trick"],
        "hands": [state["hands"][0] if player == 0 else len(state["hands"][0]),
                  state["hands"][1] if player == 1 else len(state["hands"][1])],
        "discards": state["discards"],
        "private_discards": [state["private_discards"][0] if player == 0 else len(state["private_discards"][0]),
                             state["private_discards"][1] if player == 1 else len(state["private_discards"][1])],
        "score": state["score"]
    }

if __name__ ==  '__main__':
    state = new_game()
    while len(state["hands"][0]) != 0 or len(state["hands"][1]) != 0:
        current_player = state["current_player"]
        show(state, current_player)
        if current_player == 0:
            # card_played = decode_card(input("Carte ? "))
            selected_play = random.choice(list_allowed(state, 0))
        else:
            selected_play = random.choice(list_allowed(state, 1))
        # print("Carte : {}{}".format(*selected_play[1]))
        play(state, selected_play)

    print("Résultat :")
    print("Plis gagnés : P0 {}, P1 {}".format(len(state["discards"][0])//2, len(state["discards"][1])//2))
    print("Score : P0 {}, P1 {}".format(*score(state)))