import random
from copy import copy, deepcopy
CARDS = [(a, b) for b in ["h", "s", "c"] for a in range(1, 12)]

def other_player(player):
    return 1 - player

def pick_cards(deck, num):
    cards = deck[:num]
    del deck[:num]
    return cards

def new_game(id=None):
    draw_deck = copy(CARDS)
    random.shuffle(draw_deck)
    hands = []
    for p in range(2):
        hands.append(pick_cards(draw_deck, 13))
    trump_card = pick_cards(draw_deck, 1)[0]  
    state = {
        "id": id,
        "steps": [],
        "states": [{
                    "leading_player": 0,
                    "current_player": 0,
                    "draw_deck": draw_deck,
                    "trump_card": trump_card,
                    "trick": {0: None, 1: None},
                    "hands": {0: hands[0], 1: hands[1]},
                    "discards": {0: [], 1: []},
                    "private_discards": {0: [], 1: []},
                    "score": {0: 0, 1: 0}
                   }]
    }    
    return state

def play(state, step):
    if valid_step(state, step):
        state["steps"].append(step)
        get_current_state(state)
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

def get_state(state, step_number):
    if step_number > len(state["steps"]):
        return False
    else:
        for step_n in range(step_number):
            if step_n + 1 > len(state["states"]) - 1:
                step = state["steps"][step_n]
                player = step[0]
                card = step[1]
                next_state = deepcopy(state["states"][step_n])
                action = False

                next_state["hands"][player].remove(card)
                if next_state["trick"][player] != None :
                    if next_state["trick"][player][0] == 5:
                        next_state["private_discards"][player].append(card)
                    elif next_state["trick"][player][0] == 3:
                        next_state["trump_card"] = card
                    next_state["current_player"] = other_player(player)
                else:
                    next_state["trick"][player] = card
                    next_state["current_player"] = other_player(player)

                    if card[0] == 5 and len(next_state["hands"][player]) != 0:
                        action = True
                        next_state["hands"][player].append(pick_cards(next_state["draw_deck"], 1)[0])
                        next_state["current_player"] = player
                    elif card[0] == 3 and len(next_state["hands"][player]) != 0:
                        action = True
                        next_state["hands"][player].append(next_state["trump_card"])
                        next_state["trump_card"] = None
                        next_state["current_player"] = player

                if not action:
                    if next_state["trick"][0] != None and next_state["trick"][1] != None:
                        winner, next_leading_player = trick_winner(next_state["leading_player"], next_state["trick"], next_state["trump_card"])
                        next_state["discards"][winner].append(next_state["trick"][0])
                        next_state["discards"][winner].append(next_state["trick"][1])
                        next_state["trick"] = {0: None, 1: None}
                        next_state["leading_player"] = next_leading_player
                        next_state["current_player"] = next_leading_player
                if len(next_state["hands"][0]) == 0 and len(next_state["hands"][1]) == 0:
                    next_state["score"] = score(next_state)
                state["states"].append(next_state)
        return state["states"][step_number]

def get_current_state(state):
    return get_state(state, len(state["steps"]))

def valid_step(state, step):
    current_state = get_current_state(state)
    player = step[0]
    card = step[1]
    # print(card, player, current_state)
    # print(f"testing {card}")
    if card in current_state["hands"][player]:
        # print("card in hand")
        if current_state["trick"][player] == None:
            # print("OK, no card already played for this player")
            other_card = current_state["trick"][other_player(player)]
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
                            for c in current_state["hands"][player]:
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
                    for c in current_state["hands"][player]:
                        if c[1] == other_card[1]:
                            same_suit_list.append(c)
                    if len(same_suit_list) == 0:
                        # print("OK, no card on the same suit available")
                        return True
                    else:
                        # print("NOK, play card of the same suit")
                        return False
        else:
            # print("Card already played for this player", current_state["trick"][player])
            if (state["steps"][-1][1][0] == 3 or state["steps"][-1][1][0] == 5) and state["steps"][-1][0] == player:
                return True
            else:
                return False

def score(state):
    if "steps" in state:
        current_state = get_current_state(state)
    else:
        current_state = state
    score = {0: 0, 1: 0}
    for p in range(2):
        for c in current_state["discards"][p]:
            if c[0] == 7:
                score[p] += 1
    
    tricks_won = [len(current_state["discards"][0])//2, len(current_state["discards"][1])//2]

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
        return (int(input[:-1]), input[-1])
    except ValueError:
        return False

def show(state, player):
    # print(player_state, next_action)
    current_state = get_current_state(state)
    if current_state["current_player"] == player:
        print("------------")
        print("Joueur {}".format(current_state["current_player"]))
        if current_state["trump_card"]:
            print("[**] [{}{}]".format(*current_state["trump_card"]))
        else:
            print("[**] [xx]")
        print("Pli : J0 {} / J1 {}".format(*["[{}{}]".format(c[0], c[1]) if c is not None else "[xx]" for c in [current_state["trick"][0], current_state["trick"][1]]]))
        print(" ".join(["[{}{}]".format(c[0], c[1]) for c in sorted(current_state["hands"][player], key = lambda a: (a[1], a[0]), reverse = True)]))

def list_allowed(state, player):
    current_state = get_current_state(state)
    if current_state["current_player"] == player:
        if current_state["trick"][player] != None:
            return current_state["hands"][player]
        elif current_state["trick"][0] == None and current_state["trick"][1] == None:
            return current_state["hands"][player]
        else:
            allowed = []
            other_card = current_state["trick"][other_player(player)]
            
            same_suit_list = []
            for card in current_state["hands"][player]:
                if card[1] == other_card[1]:
                    same_suit_list.append(card)
            same_suit_list.sort(key=lambda a: a[0])

            for card in current_state["hands"][player]:
                if other_card[1] == card[1]: # Same suit
                    if other_card[0] == 11: # Force best card or 1
                        if card[0] == 1:
                            # print("OK, 11 forced 1 or best")
                            allowed.append(card)
                        else:
                            if card == same_suit_list[-1]:
                                # print("OK, 11 forced 1 or best")
                                allowed.append(card)
                    else:
                        # print("OK, same suit and nothing forcing")
                        allowed.append(card)
                else: # Different suit
                    if len(same_suit_list) == 0:
                        # print("OK, no card on the same suit available")
                        allowed.append(card)
            return allowed
    else:
        return []

if __name__ ==  '__main__':
    state = new_game()
    while len(get_current_state(state)["hands"][0]) != 0 or len(get_current_state(state)["hands"][1]) != 0:
        current_state = get_current_state(state)
        current_player = current_state["current_player"]
        show(state, current_player)
        if current_player == 0:
            # card_played = decode_card(input("Carte ? "))
            card_played = random.choice(list_allowed(state, 0))
        else:
            card_played = random.choice(list_allowed(state, 1))
        # print("Carte : {}{}".format(*card_played))
        play(state, (current_player, card_played))

    current_state = get_current_state(state)
    print("Résultat :")
    print("Plis gagnés : P0 {}, P1 {}".format(len(current_state["discards"][0])//2, len(current_state["discards"][1])//2))
    print("Score : P0 {}, P1 {}".format(*score(state)))