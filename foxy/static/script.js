const urlParams = new URLSearchParams(window.location.search);

const suitHTML = {'h': ['&hearts;', 'red'],
                  's': ['&spades;', 'black'],
                  'c': ['&clubs;', 'green']};

let game_id = urlParams.get('id');
let player = -1;
let current_plays = [];

setTimeout(refresh, 1000);
// //////////////////////////////////////////////
// let button = document.createElement("button");
// button.innerHTML = "Step";
// let decks = document.getElementById("decks");
// decks.appendChild(button);
// button.addEventListener("click", refresh);
// //////////////////////////////////////////////

function refresh() {
  console.log("refresh")
  fetch(`/get_game`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify({id: game_id}),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  }).then((response) => {
    if (response.status !== 200) {
      console.log(`Looks like there was a problem. Status code: ${response.status}`);
      return;
    }
    response.json().then(async (game) => {
      await updateState(game);
      setTimeout(refresh, 1000);
    });
  });
}

async function updateState(game) {
  console.log(game);
  player = parseInt(game.player);

  if (current_plays.length == 0) {
    await setTrumpCard(game.init_trump_card);
    await setPlayerHand(game.init_hands[player]);
    sortPlayerHand();
    await setOpponentHand(game.init_hands[1 - player]);
  }
  let trump_card = game.init_trump_card;
  let special = false;
  let nbr_cards_drawn = 0;
  let trick = [];
  
  for (let [index, play] of game.plays.entries()) {
    let animate = false;
    if (index >= current_plays.length) {
      animate = true;
      current_plays.push(play);
    }
    if (play[0] === 0) {
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
  if ((window.matchMedia("(hover: hover)").matches) || (event.target.classList.contains("sel"))) {
    let card_id = event.target.id;
    fetch(`/play`, {
      method: "POST",
      credentials: "include",
      body: JSON.stringify({id: game_id, play: card_id, player: player}), // player not defined
      cache: "no-cache",
      headers: new Headers({
        "content-type": "application/json"
      })
    }).then((response) => {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then((res) => {
        // updateState(res);
      });
    }); //.then(playerPlayCard(event.target.id));
  }
  if (window.matchMedia("(hover: none)").matches) {
    if ([1,3,5,7,9,11].includes(hand[i][0])) {
      helpdiv = document.getElementById("help"+hand[i][0]);
      helpdiv.classList.remove("hidden");
    }
    event.target.classList.toggle("sel");
  }
}

async function moveCard(card, start, target, stay=false, replace=false, remove_start=false) {
  let start_position = start.getBoundingClientRect();
  if (remove_start) {
    start.parentNode.removeChild(start);
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
      anim.parentNode.removeChild(anim);
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

async function setTrumpCard(trump_card) {
  let trump = document.getElementById("trump").children[0];
  let deck = document.getElementById("deck");
  if (trump_card != null) {
    id = trump_card[0] + trump_card[1];
    if (trump.id != id) {
      await moveCard(getCard(trump_card, id), deck, trump, stay=false, replace=true);
    }
  } else {
    trump = getCard("empty", "empty");
  }
}

async function setOpponentHand(hand) {
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
      if (i == hand.length-1) {
        await moveCard(card, deck, opponenthand, stay=true);
      } else {
        moveCard(card, deck, opponenthand, stay=true);
      }
    }
  }
}

async function setPlayerHand(hand) {
  let playerhand = document.getElementById("playerhand");
  let deck = document.getElementById("deck");

  let children = playerhand.children;
  let list_ids = [];
  for (let i = 0; i < hand.length; i++) {
    let id = hand[i][0] + hand[i][1];
    list_ids.push(id);
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
      card.addEventListener("click", playCard);
      if (i == hand.length-1) {
        await moveCard(card, deck, playerhand, stay=true);
      } else {
        moveCard(card, deck, playerhand, stay=true);
      }
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
  await moveCard(card, card, target, stay=false, replace=true, remove_start=true);
  card.id = "pt";
  card.classList.remove("selectable");
  card.removeEventListener("click", playCard);
}

async function opponentPlayCard(c) {
  let hand = document.getElementById("opponenthand").children[0];
  let target = document.getElementById("ot");
  let card = getCard(c, cardToId(c));
  await moveCard(card, hand, target, stay=false, replace=true, remove_start=true);
  card.id = "ot";
  hand.removeChild(hand.children[0]);
}

async function playerDrawCard(c) {
  let playerhand = document.getElementById("playerhand");
  let deck = document.getElementById("deck");
  let card = getCard(c, cardToId(c));
  card.classList.add("selectable");
  card.addEventListener("click", playCard);
  await moveCard(card, deck, playerhand, stay=true);
}

async function opponentDrawCard() {
  let opponenthand = document.getElementById("opponenthand");
  let deck = document.getElementById("deck");
  let card = getCard("back");
  await moveCard(card, deck, opponenthand, stay=true);
}

async function playerDiscardCard(c) {
  let target = document.getElementById("deck");
  let card = document.getElementById(cardToId(c));
  await moveCard(card, card, target, stay=false, replace=false, remove_start=true);
}

async function opponentDiscardCard() {
  // let opponenthand = document.getElementById("opponenthand").children[0];
  let deck = document.getElementById("deck");
  let card = getCard("back");
  await moveCard(card, card, deck, stay=false, replace=false, remove_start=true);
}

async function playerDrawTrump() {
  let playerhand = document.getElementById("playerhand");
  let trump = document.getElementById("trump").children[0];
  let c =  IdToCard(trump.id);
  let card = getCard(c, cardToId(c));
  card.classList.add("selectable");
  card.addEventListener("click", playCard);
  await moveCard(card, trump, playerhand, stay=true);
  trump.replaceWith(getCard("empty", "empty"));
}

async function opponentDrawTrump() {
  let opponenthand = document.getElementById("opponenthand");
  let trump = document.getElementById("trump").children[0];
  let card = getCard("back");
  await moveCard(card, trump, opponenthand, stay=true);
  trump.replaceWith(getCard("empty", "empty"));
}

async function playerPlayTrump(c) {
  let source = document.getElementById(cardToId(c));
  let trump = document.getElementById("trump").children[0];
  let card = getCard(c, cardToId(c));
  await moveCard(card, source, trump, stay=false, replace=true, remove_start=true);
}

async function opponentPlayTrump(c) {
  let hand = document.getElementById("opponenthand").children[0];
  let trump = document.getElementById("trump").children[0];
  let card = getCard(c, cardToId(c));
  await moveCard(card, hand, trump, stay=false, replace=true, remove_start=true);
}

async function clearTrick(winner) {
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
          helpdiv = document.getElementById("help"+value);
          helpdiv.classList.add("hidden");
        }
        selected_cards[i].classList.remove("sel");
      }
    }
  });
}