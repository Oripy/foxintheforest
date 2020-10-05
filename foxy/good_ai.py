from foxy.foxintheforest import new_game, play, pick_cards, other_player, get_player_state, list_allowed, CARDS, COLORS
from random import shuffle, choice
from copy import copy, deepcopy
from math import sqrt, log

K = 5
NB_SIMUL_P0 = 5000

class Node():
  """ The Node object is one node of the Monte Carlo tree
  Args:
    play (list): this list describe the play that lead to this node [player, [card_value, card_suit]]
    parent (Node): the parent of this node (default: None for the root of the tree)

  Attributes:
    play (list): this list describe the play that lead to this node [player, [card_value, card_suit]]
    parent (Node): the parent of this node (default: None for the root of the tree)
    availability: number of time this node was a possible move to play
    visits: number of time this node was visited during the search
    reward: total reward received by this node
    children: list of children nodes
  """
  def __init__(self, play, parent=None):
    if play != None:
      self.play = [play[0], play[1]]
    else:
      self.play = None
    self.parent = parent
    self.availability = 0
    self.visits = 0
    self.reward = 0
    self.children = []
    self.outcome_p0 = {"humble": 0, "defeated":0, "victorious":0, "greedy":0}
  
  def add_child(self, node):
    self.children.append(node)
  
  def __repr__(self):
    sum = self.outcome_p0["humble"] + self.outcome_p0["defeated"] + self.outcome_p0["victorious"] + self.outcome_p0["greedy"]
    if sum == 0:
      sum = 1
    return f"""{self.play} visits:{self.visits} reward:{self.reward} av.:{self.availability} h:{self.outcome_p0["humble"]/sum*100:.2f}%,d:{self.outcome_p0["defeated"]/sum*100:.2f}%,v:{self.outcome_p0["victorious"]/sum*100:.2f}%,g:{self.outcome_p0["greedy"]/sum*100:.2f}% : V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/sum*100:.2f}"""

  def show(self, indent=0, depth=1):
    """ print the tree in the console starting at this node with the given depth """
    text = "  "*indent
    sum = self.outcome_p0["humble"] + self.outcome_p0["defeated"] + self.outcome_p0["victorious"] + self.outcome_p0["greedy"]
    if sum == 0:
      sum = 1
    text += f"""{self.play} visits:{self.visits} reward:{self.reward} av.:{self.availability} h:{self.outcome_p0["humble"]/sum*100:.2f}%,d:{self.outcome_p0["defeated"]/sum*100:.2f}%,v:{self.outcome_p0["victorious"]/sum*100:.2f}%,g:{self.outcome_p0["greedy"]/sum*100:.2f}% : V:{(self.outcome_p0["victorious"]+self.outcome_p0["humble"])/sum*100:.2f}"""
    print(text)
    if depth > 0:
      for c in sorted(self.children, key=lambda a:a.visits, reverse=True):
        c.show(indent=indent+1, depth=depth-1)
  
def UCT(node):
  """ output Upper Confidence Bound formula result for the given node """
  return node.reward / node.visits + K * sqrt(log(node.availability) / node.visits)

def copy_state(state):
  """ output a cloned copy of the given state """
  plays = []
  for p in state["plays"]:
    if len(p) == 2:
      plays.append([p[0], p[1]])
    else:
      plays.append([p[0], p[1], p[2]])
  hands = []
  if isinstance(state["hands"][0], int):
    hands.append(state["hands"][0])
  else:
    hands.append(state["hands"][0].copy())
  if isinstance(state["hands"][1], int):
    hands.append(state["hands"][1])
  else:
    hands.append(state["hands"][1].copy())
  discards = []
  discards.append(state["discards"][0].copy())
  discards.append(state["discards"][1].copy())
  private_discards  = []
  if isinstance(state["private_discards"][0], int):
    private_discards.append(state["private_discards"][0])
  else:
    private_discards.append(state["private_discards"][0].copy())
  if isinstance(state["private_discards"][1], int):
    private_discards.append(state["private_discards"][1])
  else:
    private_discards.append(state["private_discards"][1].copy())
  
  return {
    "plays": plays,
    "player": state["player"],
    "leading_player": state["leading_player"],
    "current_player": state["current_player"],
    "trump_card": state["trump_card"],
    "trick": [state["trick"][0], state["trick"][1]],
    "hands": hands,
    "discards": discards,
    "private_discards": private_discards,
    "score": [state["score"][0], state["score"][1]]
  }

def aquire_knowledge(state):
  """ Extract knowledge on current state from past plays """
  remaining_cards = [c for c in CARDS if c not in state["hands"][state["current_player"]] if c not in state["discards"][0] if c not in state["discards"][1] if c not in state["private_discards"][state["current_player"]] if c != state["trump_card"]]
  draw_deck = []
  opponent_hand = []
  opponent_cuts = []
  opponent_max_one = []

  trick = []
  next_special = False
  for p in state["plays"]:
    if p[0] == other_player(state["player"]) and p[1] in opponent_hand:
      opponent_hand.remove(p[1])
    elif p[1] in remaining_cards:
      remaining_cards.remove(p[1])
    if next_special:
      next_special = False
    else:
      if len(trick) == 2:
        trick = []
      if len(trick) == 0:
        trick.append(p)
      elif len(trick) == 1:
        trick.append(p)
        if trick[0][0] == state["player"]:
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
      if p[1][0] == 5:
        if p[0] == other_player(state["player"]):
          for cut in opponent_cuts:
            if cut not in opponent_max_one:
              opponent_max_one += opponent_cuts
            else:
              opponent_max_one.remove(cut)
          opponent_cuts = []
          opponent_hand = []
          remaining_cards += draw_deck
          draw_deck = []
        else:
          if p[2] in draw_deck:
            draw_deck.remove(p[2])
        next_special = True
      if p[1][0] == 3:
        if p[0] == other_player(state["player"]):
          opponent_hand.append(p[2])
        next_special = True
  remaining_cards = [c for c in remaining_cards if c not in draw_deck]
  for cut in opponent_cuts:
    draw_deck += [c for c in remaining_cards if c[1] == cut]
    remaining_cards = [c for c in remaining_cards if c[1] != cut]

  return {
    "remaining_cards": remaining_cards,
    "draw_deck": draw_deck,
    "opponent_hand": opponent_hand,
    "opponent_max_one": opponent_max_one
  }

def random_state(state, knowledge):
  """ output a possible random state with the given knowledge """
  s = copy_state(state)
  remaining_cards = [c for c in knowledge["remaining_cards"]]
  draw_deck = [c for c in knowledge["draw_deck"]]
  opponent_hand = [c for c in knowledge["opponent_hand"]]
  opponent_max_one = [c for c in knowledge["opponent_max_one"]]
  shuffle(remaining_cards)
  nbr_unknown_cards_opp_hand = s["hands"][other_player(s["current_player"])] - len(opponent_hand)
  for _ in range(nbr_unknown_cards_opp_hand):
    opponent_hand += pick_cards(remaining_cards, 1)
    if opponent_hand[-1][1] in opponent_max_one:
      opponent_max_one.remove(opponent_hand[-1][1])
      draw_deck += [c for c in remaining_cards if c[1] == opponent_hand[-1][1]]
      remaining_cards = [c for c in remaining_cards if c[1] != opponent_hand[-1][1]]
  s["hands"][other_player(s["current_player"])] = opponent_hand
  s["private_discards"][other_player(s["current_player"])] = pick_cards(remaining_cards, s["private_discards"][other_player(s["current_player"])])
  s["draw_deck"] = draw_deck + remaining_cards
  return s

def select(node, state, ai_player):
  """ Select one of the allowed children based on UCT calculation """
  allowed = list_allowed(state, state["current_player"])
  shuffle(allowed)
  list_children = []
  for p in allowed:
    exists = False
    for n in node.children:
      if p[0] == n.play[0] and p[1] == n.play[1]:
        exists = True
        list_children.append(n)
        break
    if not exists:
      new_child = Node(p, node)
      node.add_child(new_child)
      list_children.append(new_child)
    
  if ai_player == state["current_player"]: 
    min_max = 0
  else:
    min_max = float("inf")
  selected = None
  for n in list_children:
    n.availability += 1
  for n in list_children:
    if n.visits == 0:
      selected = n
      break
    else:
      value = UCT(n)
      if ai_player == state["current_player"]: 
        if value > min_max:
          min_max = value
          selected = n
      else:
        if value < min_max:
          min_max = value
          selected = n
  return selected

def select_play(state, runs):
  """ Select one play based on MCTS simulations """
  allowed = list_allowed(state, state["current_player"])
  if len(allowed) == 1:
    return allowed[0]

  root = Node(None)
  player = state["current_player"]
  k = aquire_knowledge(state)
  for _ in range(runs):
    s = random_state(state, k)
    node = root
    while len(s["hands"][0]) != 0 or len(s["hands"][1]) != 0:
      node = select(node, s, player)
      play(s, node.play)
    while node.parent != None:
      node.visits += 1
      tricks_won = len(s["discards"][0])//2
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
    
  maxi = 0
  selected = None
  for n in root.children:
    if n.visits > maxi:
      selected = n
      maxi = n.visits

  return selected.play

def ia_play(state):
  """ Select a play and return it """
  return select_play(state, NB_SIMUL_P0)
