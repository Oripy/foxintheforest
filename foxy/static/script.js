const urlParams = new URLSearchParams(window.location.search);
const url = new URL(window.location);
const socket = io();

const suitHTML = {'h': ['&hearts;', 'red'],
                  's': ['&spades;', 'black'],
                  'c': ['&clubs;', 'green']};

let game_id = urlParams.get('id');
let current_plays = 0;
let current_game;
if (urlParams.has('play')) {
  current_plays = urlParams.get('play');
}
let player = -1;

window.onpopstate = (event) => {
  current_plays = event.state['play'];
  console.log(current_plays);
  showState(current_game);
};

socket.on('connect', () => socket.emit('get game', JSON.stringify({id: game_id})));
socket.on('error', (error) => console.error('SocketIO error ', error));
socket.on('game', (game) => showState(JSON.parse(game)));
socket.on('game state', (game) => Queue.enqueue(() => updateState(JSON.parse(game))));
socket.on('message', (data) => showMessage(JSON.parse(data).text, JSON.parse(data).category));

document.getElementById("playerhand").addEventListener("click", playCard);

function showMessage(text, category) {
  let message_div = document.getElementById("messages");
  let message = document.createElement("div");
  message.classList.add("alert", category);
  message.innerHTML = text;
  message_div.appendChild(message);
  setTimeout(() => {
    message.addEventListener("transitionend", (e) => e.currentTarget.remove());
    message.style.transform = `translate(0px, ${message.clientHeight}px)`;
    message.style.opacity = 0;
  }, 4000);
}

function removeCardFromHand(hand, card) {
  return hand.filter(function(c){ 
    return (c[0] != card[0] || c[1] != card[1]); 
  });
}

function showState(game) {
  console.log(game);
  player = parseInt(game.player);
  current_game = game;
  let trump_card = game.init_trump_card;
  let player_hand = [...game.init_hands[player]];
  let opponent_hand = [...game.init_hands[1 - player]];
  let deck = [...game.init_draw_deck];
  let special = false;
  let trick = [];

  current_plays = Math.min(game.plays.length, current_plays);
  document.getElementById("playerscore").innerHTML = 0;
  document.getElementById("opponentscore").innerHTML = 0;
  
  for (let play of game.plays.slice(0, current_plays)) {
    console.log(play);
    if (play[0] === player) {
      switch (special) {
        case false:
          player_hand = removeCardFromHand(player_hand, play[1]);
          trick.push(play);
          if (play[1][0] == 3) {
            player_hand.push(trump_card);
            trump_card = null;
            special = 3;
          } else if (play[1][0] == 5) {
            player_hand.push(deck[0]);
            deck.shift();
            special = 5;
          }
          break;
        case 3:
          special = false;
          player_hand = removeCardFromHand(player_hand, play[1]);
          trump_card = play[1];
          break;
        case 5:
          special = false;
          player_hand = removeCardFromHand(player_hand, play[1]);
          break;
      }
    } else {
      switch (special) {
        case false:
          opponent_hand.pop();
          trick.push(play);
          if (play[1][0] == 3) {
            opponent_hand.push([null, null]);
            trump_card = null;
            special = 3;
          } else if (play[1][0] == 5) {
            opponent_hand.push([null, null]);
            special = 5;
          }
          break;
        case 3:
          special = false;
          opponent_hand.pop();
          trump_card = play[1];
          break;
        case 5:
          special = false;
          opponent_hand.pop();
          break;
      }
    }
    if (trick.length >= 2 && !special) {
      let cardp0 = (trick[0][0] == 0) ? trick[0][1] : trick[1][1];
      let cardp1 = (trick[0][0] == 1) ? trick[0][1] : trick[1][1];
      let winner = trickwinner(trick[0][0], cardp0, cardp1, trump_card);
      if (winner == player) {
        document.getElementById("playerscore").innerHTML++;
      } else {
        document.getElementById("opponentscore").innerHTML++;
      }
      trick = [];
    }
  }
  setTrumpCard(trump_card);
  setPlayerHand(player_hand);
  sortPlayerHand();
  setOpponentHand(opponent_hand);
  document.getElementById('pt').replaceWith(getCard('empty', 'pt'));
  document.getElementById('ot').replaceWith(getCard('empty', 'ot'));
  for (let p of trick) {
    if (p[0] == player) {
      document.getElementById('pt').replaceWith(getCard(p[1], 'pt'));
    } else {
      document.getElementById('ot').replaceWith(getCard(p[1], 'ot'));
    }
  }
  
  if (game.plays.length > current_plays) {
    Queue.enqueue(() => updateState(game));
  }
}

async function updateState(game) {
  console.log(game);
  current_game = game;
  // player = parseInt(game.player);

  // if (current_plays == 0) {
  //   await setTrumpCard(game.init_trump_card);
  //   await setPlayerHand(game.init_hands[player]);
  //   await setOpponentHand(game.init_hands[1 - player]);
  //   sortPlayerHand();
  // }
  let trump_card = game.init_trump_card;
  let special = false;
  let nbr_cards_drawn = 0;
  let trick = [];
  
  for (let [index, play] of game.plays.entries()) {
    let animate = false;
    if (index >= current_plays) {
      animate = true;
      current_plays++;
      urlParams.set('play', current_plays);
      url.searchParams.set('play', current_plays);
      history.pushState({'play': current_plays}, '', url);
    }
    if (play[0] === player) {
      switch (special) {
        case false:
          if (animate) await playerPlayCard(play[1]);
          trick.push(play);
          if (play[1][0] == 3) {
            if (animate) await playerDrawTrump();
            special = 3;
          } else if (play[1][0] == 5) {
            if (animate) await playerDrawCard(game.init_draw_deck[nbr_cards_drawn]);
            if (animate) sortPlayerHand();
            nbr_cards_drawn += 1;
            special = 5;
          }
          break;
        case 3:
          special = false;
          if (animate) await playerPlayTrump(play[1]);
          trump_card = play[1];
          break;
        case 5:
          special = false;
          if (animate) await playerDiscardCard(play[1]);
          break;
      }
    } else {
      switch (special) {
        case false:
          if (animate) await opponentPlayCard(play[1]);
          trick.push(play);
          if (play[1][0] == 3) {
            if (animate) await opponentDrawTrump();
            special = 3;
          } else if (play[1][0] == 5) {
            if (animate) await opponentDrawCard();
            nbr_cards_drawn += 1;
            special = 5;
          }
          break;
        case 3:
          special = false;
          if (animate) await opponentPlayTrump(play[1]);
          trump_card = play[1];
          break;
        case 5:
          special = false;
          if (animate) await opponentDiscardCard();
          break;
      }
    }
    if (trick.length >= 2 && !special) {
      let cardp0 = (trick[0][0] == 0) ? trick[0][1] : trick[1][1];
      let cardp1 = (trick[0][0] == 1) ? trick[0][1] : trick[1][1];
      let winner = trickwinner(trick[0][0], cardp0, cardp1, trump_card);
      if (animate) await clearTrick(winner);
      trick = [];
    }
  }
}

function trickwinner(leading_player, cardp0, cardp1, trump) {
  let winner = undefined;
  let trump_suit = trump[1];
  let cardp0_suit = cardp0[1];
  let cardp1_suit = cardp1[1];
  let cardp0_value = cardp0[0];
  let cardp1_value = cardp1[0]; 
  if (cardp0_value == 9) {
    if (cardp1_value != 9) {
      cardp0_suit = trump_suit;
    }
  }
  if (cardp1_value == 9) {
    if (cardp0_value != 9) {
      cardp1_suit = trump_suit;
    }
  }
  if (cardp0_suit == cardp1_suit) {
    winner = (cardp0_value > cardp1_value) ? 0 : 1;
  } else {
    if (cardp0_suit == trump_suit) {
      winner = 0;
    } else if (cardp1_suit == trump_suit) {
      winner = 1;
    } else {
      winner = leading_player;
    }
  }
  return winner
}

function cardToId(card) {
  return card.join(''); 
}

function IdToCard(id) {
  return [parseInt(id.slice(0, -1)), id.slice(-1)]; 
}

function playCard(event) {
  if (event.target && event.target.matches(".playingcard")) {
    if ((window.matchMedia("(hover: hover)").matches) || (event.target.classList.contains("sel"))) {
      let card_id = event.target.id;
      socket.emit("play", JSON.stringify({id: game_id, play: card_id, player: player}))
      if (window.matchMedia("(hover: none)").matches) {
        let value = parseInt(event.target.id.slice(0, -1));
        if ([1,3,5,7,9,11].includes(value)) {
          let helpdiv = document.getElementById("help"+value);
          console.log(helpdiv);
          helpdiv.classList.add("hidden");
        }
      }
    }
    else if (window.matchMedia("(hover: none)").matches) {
      let value = parseInt(event.target.id.slice(0, -1));
      if ([1,3,5,7,9,11].includes(value)) {
        let helpdiv = document.getElementById("help"+value);
        helpdiv.classList.remove("hidden");
      }
      event.target.classList.toggle("sel");
    }
  }
}

async function moveCard(card, start, target, stay=false, replace=false, remove_start=false) {
  let start_position = start.getBoundingClientRect();
  if (remove_start) {
    start.remove();
  }
  let anim = card.cloneNode(true);

  let target_position;
  if (stay) {
    target.appendChild(card);
    card.style.visibility = "hidden";
    target_position = card.getBoundingClientRect();
  } else {
    target_position = target.getBoundingClientRect();
  }

  document.body.appendChild(anim);
  anim.style.position = "absolute";
  anim.style.top = start_position.top + "px";
  anim.style.left = start_position.left + "px";
  await new Promise(resolve => setTimeout(resolve, 100));
  return new Promise(resolve => {
    let onTransitionEndCb = () => {
      if (stay) {
        card.style.visibility = "visible";
      }
      if (replace) {
        target.replaceWith(card);
      }
      anim.remove();
      anim.removeEventListener('transitionend', onTransitionEndCb);
      resolve('resolved');
    }
    anim.addEventListener('transitionend', onTransitionEndCb);
    anim.style.transition = ".5s";
    anim.style.transitionTimingFunction = "linear";
    anim.style.top = target_position.top + "px";
    anim.style.left = target_position.left + "px";
  });
}

function cardHTML(card) {
  if ((card == "empty") || (card == "back")) {
    return "&nbsp;<br />&nbsp;";
  } else {
    return card[0]+"<br />"+suitHTML[card[1]][0];
  }
}

function getCard(card, id=undefined) {
  let div = document.createElement("div");
  div.innerHTML = cardHTML(card);
  div.classList.add("playingcard");
  switch (card) {
    case 'back':
      div.classList.add("back");
      break;
    case 'empty':
      div.classList.add("empty");
      break;
    default:
      div.classList.add(suitHTML[card[1]][1]);
  }
  if (id) div.id = id;
  return div;
}

function setTrumpCard(trump_card) {
  let trump = document.getElementById("trump").children[0];
  if (trump_card != null) {
    let id = cardToId(trump_card);
    if (trump.id != id) {
      console.log(id, getCard(trump_card, id));
      trump.replaceWith(getCard(trump_card, id));
    }
  } else {
    trump.replaceWith(getCard("empty", "empty"));
  }
}

function setOpponentHand(hand) {
  let opponenthand = document.getElementById("opponenthand");
  let children = opponenthand.children;
  if (children.length > hand.length) {
    for (let i = 0; i < children.length - hand.length; i++) {
      opponenthand.removeChild(opponenthand.children[0]);
    }
  }
  if (children.length < hand.length) { 
    for (let i = children.length; i < hand.length; i++) {
      let card = getCard("back");
      opponenthand.appendChild(card);
    }
  }
}

function setPlayerHand(hand) {
  let playerhand = document.getElementById("playerhand");

  let children = playerhand.children;
  let list_ids = [];
  for (let i = 0; i < hand.length; i++) {
    list_ids.push(cardToId(hand[i]));
  }
  for (let i = 0; i < children.length; i++) {
    if (list_ids.includes(children[i].id)) {
      list_ids.splice(list_ids.indexOf(children[i].id), 1);
    } else {
      playerhand.removeChild(children[i]);
    }
  }
  for (let i = 0; i < hand.length; i++) {
    let id = cardToId(hand[i]);
    if (list_ids.includes(id)) {
      let card = getCard(hand[i], id);
      card.classList.add("selectable");
      playerhand.appendChild(card);
    }
  }
}

async function sortPlayerHand() {
  let playerhand = document.getElementById("playerhand");
  [...playerhand.children]
    .sort((a, b) => {
      let a1 = parseInt(a.id.slice(0, -1));
      let a2 = a.id.slice(-1);
      let b1 = parseInt(b.id.slice(0, -1));
      let b2 = b.id.slice(-1);
      if (a2 > b2) {
        return -1;
      } else if (a2 < b2) {
        return 1;
      } else {
        if (a1 > b1) {
          return 1;
        } 
        if (a1 < b1) {
          return -1;
        }
      }
    })
    .forEach(node=>playerhand.appendChild(node)); 
}

async function playerPlayCard(c) {
  let target = document.getElementById("pt");
  let card = document.getElementById(cardToId(c));
  await moveCard(card, card, target, false, true, true);
  card.id = "pt";
  card.classList.remove("selectable");
}

async function opponentPlayCard(c) {
  let hand = document.getElementById("opponenthand").children[0];
  let target = document.getElementById("ot");
  let card = getCard(c, cardToId(c));
  await moveCard(card, hand, target, false, true, true);
  card.id = "ot";
  hand.removeChild(hand.children[0]);
}

async function playerDrawCard(c) {
  let playerhand = document.getElementById("playerhand");
  let deck = document.getElementById("deck");
  let card = getCard(c, cardToId(c));
  card.classList.add("selectable");
  await moveCard(card, deck, playerhand, true);
}

async function opponentDrawCard() {
  let opponenthand = document.getElementById("opponenthand");
  let deck = document.getElementById("deck");
  let card = getCard("back");
  await moveCard(card, deck, opponenthand, true);
}

async function playerDiscardCard(c) {
  let target = document.getElementById("deck");
  let card = document.getElementById(cardToId(c));
  await moveCard(card, card, target, false, false, true);
}

async function opponentDiscardCard() {
  let opponentcard = document.getElementById("opponenthand").children[0];
  let deck = document.getElementById("deck");
  let card = getCard("back");
  await moveCard(card, opponentcard, deck, false, false, true);
}

async function playerDrawTrump() {
  let playerhand = document.getElementById("playerhand");
  let trump = document.getElementById("trump").children[0];
  let c =  IdToCard(trump.id);
  let card = getCard(c, cardToId(c));
  card.classList.add("selectable");
  await moveCard(card, trump, playerhand, true);
  trump.replaceWith(getCard("empty", "empty"));
}

async function opponentDrawTrump() {
  let opponenthand = document.getElementById("opponenthand");
  let trump = document.getElementById("trump").children[0];
  let card = getCard("back");
  await moveCard(card, trump, opponenthand, true);
  trump.replaceWith(getCard("empty", "empty"));
}

async function playerPlayTrump(c) {
  let source = document.getElementById(cardToId(c));
  let trump = document.getElementById("trump").children[0];
  let card = getCard(c, cardToId(c));
  await moveCard(card, source, trump, false, true, true);
}

async function opponentPlayTrump(c) {
  let hand = document.getElementById("opponenthand").children[0];
  let trump = document.getElementById("trump").children[0];
  let card = getCard(c, cardToId(c));
  await moveCard(card, hand, trump, false, true, true);
}

async function clearTrick(winner) {
  let target;
  if (winner == player) {
    target = document.getElementById("playername");
  } else {
    target = document.getElementById("opponentname");
  }
  let card1 = document.getElementById("ot");
  let card2 = document.getElementById("pt");
  moveCard(card1, card1, target);
  await moveCard(card2, card2, target);
  card1.replaceWith(getCard("empty", "ot"));
  card2.replaceWith(getCard("empty", "pt"));
  if (winner == player) {
    document.getElementById("playerscore").innerHTML++;
  } else {
    document.getElementById("opponentscore").innerHTML++;
  }
}

if (window.matchMedia("(hover: none)").matches) {
  document.addEventListener("click", (event) => {
    let selected_cards = document.getElementsByClassName("sel");
    for (let i = 0; i < selected_cards.length; i++) {
      if (! selected_cards[i].contains(event.target)) {
        let value = parseInt(selected_cards[i].id.slice(0, -1));
        if ([1,3,5,7,9,11].includes(value)) {
          let helpdiv = document.getElementById("help"+value);
          helpdiv.classList.add("hidden");
        }
        selected_cards[i].classList.remove("sel");
      }
    }
  });
}

if (window.matchMedia("(hover: hover)").matches) {
  document.addEventListener("mouseover", (event) => {
    if (event.target.classList.contains("playingcard")) {
      let value = parseInt(event.target.id.slice(0, -1));
      if ([1,3,5,7,9,11].includes(value)) {
        let helpdiv = document.getElementById("help"+value);
        helpdiv.classList.remove("hidden");
        event.target.addEventListener("mouseleave", () => {
          helpdiv.classList.add("hidden");
        }, {once: true});
      }
    }
  });
}
