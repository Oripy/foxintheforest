const urlParams = new URLSearchParams(window.location.search);

let game_id = urlParams.get('id');
let prev_hand = [];
let current_play_number = -1;
setTimeout(refresh, 1000);

function refresh() {
  fetch(`/state`, {
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
    response.json().then((res) => {
      updateState(res);
      setTimeout(refresh, 1000);
    });
  });
}

function updateState(state) {
  if (state.plays.length == current_play_number) {
    return false
  }
  for (let  i= 1; i < 12; i+=2) {
    helpdiv = document.getElementById("help"+i);
    helpdiv.classList.add("hidden");
  }
  current_play_number = state.plays.length;
  player = parseInt(state.player)
  if (state.plays.length > 0) {
    card_played = state.plays[state.plays.length-1][1];
  } else {
    card_played = [undefined, undefined];
  }
  if (state.plays.length > 1) {
    prev_card_played = state.plays[state.plays.length-2][1];
  } else {
    prev_card_played = [undefined, undefined];
  }
  let opponenthand = document.getElementById("opponenthand");
  while (opponenthand.firstChild) {
    opponenthand.removeChild(opponenthand.firstChild);
  }
  for (let i = 0; i < state.hands[1 - player]; i++) {
    let card = document.createElement("div");
    card.innerHTML = cardHTML("empty");
    card.className = "playingcard back";
    card.id = "oh"+i;
    opponenthand.appendChild(card);
  }

  let trump = document.getElementById("trump");
  if (state.trump_card != null) {
    trump.innerHTML = cardHTML(state.trump_card);
    trump.className = "playingcard";
    trump.classList.add(suitHTML[state.trump_card[1]][1]);
    if ((state.trump_card[0] == card_played[0]) && (state.trump_card[1] == card_played[1])) {
      trump.classList.add("highlight");
    }
  } else {
    trump.innerHTML = cardHTML("empty");
    trump.className = "playingcard empty";
  }

  let ot = document.getElementById("ot");
  if (state.trick[1 - player] != null) {
    ot.innerHTML = cardHTML(state.trick[1 - player]);
    ot.className = "playingcard";
    ot.classList.add(suitHTML[state.trick[1 - player][1]][1]);
    if ((state.trick[1 - player][0] == card_played[0]) && (state.trick[1 - player][1] == card_played[1])) {
      ot.classList.add("highlight");
    }
  } else {
    ot.innerHTML = cardHTML("empty");
    ot.className = "playingcard empty";
  }

  let pt = document.getElementById("pt");
  if (state.trick[player] != null) {
    pt.innerHTML = cardHTML(state.trick[player]);
    pt.className = "playingcard";
    pt.classList.add(suitHTML[state.trick[player][1]][1]);
    if ((state.trick[player][0] == card_played[0]) && (state.trick[player][1] == card_played[1])) {
      pt.classList.add("highlight");
    }
  } else {
    pt.innerHTML = cardHTML("empty");
    pt.className = "playingcard empty";
  }

  let pscore = document.getElementById("playerscore");
  pscore.innerHTML = Math.floor(state.discards[player].length/2);
  let oscore = document.getElementById("opponentscore");
  oscore.innerHTML = Math.floor(state.discards[1 - player].length/2);

  let plasttrick = document.getElementById("plasttrick");
  let pdiscardlength = state.discards[player].length;
  while (plasttrick.firstChild) {
    plasttrick.removeChild(plasttrick.firstChild);
  }

  if (pdiscardlength >= 2) {
    let show_last_trick = false;
    for (let i = 0; i < 2; i++) {
      cardvalue = state.discards[player][pdiscardlength-2+i];
      if ((((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) || ((cardvalue[0] == prev_card_played[0]) && (cardvalue[1] == prev_card_played[1])))) {
        show_last_trick = true;
      }
    }
    if (show_last_trick) {
      for (let i = 0; i < 2; i++) {
        let card = document.createElement("div");
        cardvalue = state.discards[player][pdiscardlength-2+i];
        card.innerHTML = cardHTML(cardvalue);
        card.className = "playingcard";
        card.classList.add(suitHTML[cardvalue[1]][1]);
        if ((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) {
          card.classList.add("highlight");
        }
        plasttrick.appendChild(card);
      }
    }
  }

  let olasttrick = document.getElementById("olasttrick");
  let odiscardlength = state.discards[1 - player].length;
  while (olasttrick.firstChild) {
    olasttrick.removeChild(olasttrick.firstChild);
  }
  if (odiscardlength >= 2) {
    let show_last_trick = false;
    for (let i = 0; i < 2; i++) {
      cardvalue = state.discards[1 - player][odiscardlength-2+i];
      if (((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) || ((cardvalue[0] == prev_card_played[0]) && (cardvalue[1] == prev_card_played[1]))) {
        show_last_trick = true;
      }
    }
    if (show_last_trick) {
      for (let i = 0; i < 2; i++) {
        let card = document.createElement("div");
        cardvalue = state.discards[1 - player][odiscardlength-2+i];
        card.innerHTML = cardHTML(cardvalue);
        card.className = "playingcard";
        card.classList.add(suitHTML[cardvalue[1]][1]);
        if ((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) {
          card.classList.add("highlight");
        }
        olasttrick.appendChild(card);
      }
    }
  }

  let playerhand = document.getElementById("playerhand");
  while (playerhand.firstChild) {
    playerhand.removeChild(playerhand.firstChild);
  }
  let hand = state.hands[player].sort((a, b) => {
		if (a[1] > b[1]) {
			return -1;
		} else if (a[1] < b[1]) {
			return 1;
		} else {
			if (a[0] == "Q") return 1;
			if (a[0] == "A") return -1;
			if (b[0] == "Q") return -1;
			if (b[0] == "A") return 1;
			if (a[0] > b[0]) return 1;
			if (a[0] < b[0]) return -1;
    }
  });
  for (let i = 0; i < hand.length; i++) {
    let card = document.createElement("div");
    card.innerHTML = cardHTML(hand[i]);
    card.classList.add("playingcard");
    card.classList.add("selectable");
    card.classList.add(suitHTML[hand[i][1]][1]);
    card.classList.add("highlight");
    for (let c of prev_hand) {
      if ((hand[i][0] == c[0]) && (hand[i][1] == c[1])) {
        card.classList.remove("highlight");
      }
    }
    card.id = hand[i][0] + hand[i][1];
    playerhand.appendChild(card);
    if (window.matchMedia("(hover: hover)").matches) {
      if ([1,3,5,7,9,11].includes(hand[i][0])) {
        card.addEventListener("mouseover", event => {
          helpdiv = document.getElementById("help"+hand[i][0]);
          helpdiv.classList.remove("hidden");
        });
        card.addEventListener("mouseleave", event => {
          helpdiv = document.getElementById("help"+hand[i][0]);
          helpdiv.classList.add("hidden");
        });
      }
    }
    if (state.current_player == player) {
      card.addEventListener("click", (event) => {
        if ((window.matchMedia("(hover: hover)").matches) || (event.target.classList.contains("sel"))) {
          let card_id = event.target.id;
          fetch(`/play`, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify({id: game_id, play: card_id, player: player}),
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
              updateState(res);
            });
          });
        }
        if (window.matchMedia("(hover: none)").matches) {
          if ([1,3,5,7,9,11].includes(hand[i][0])) {
            helpdiv = document.getElementById("help"+hand[i][0]);
            helpdiv.classList.remove("hidden");
          }
          event.target.classList.toggle("sel");
        }
      });
    }
  }

  let playername = document.getElementById("playername");
  let opponentname = document.getElementById("opponentname");
  if (state.current_player == player) {
    playername.classList.add("select")
    opponentname.classList.remove("select")
  } else {
    playername.classList.remove("select")
    opponentname.classList.add("select")
  }

  prev_hand = hand;
}

const suitHTML = {'h': ['&hearts;', 'red'],
                  's': ['&spades;', 'black'],
                  'c': ['&clubs;', 'green']};

function cardHTML(card) {
  if (card == "empty") {
    return "&nbsp;<br />&nbsp;";
  } else {
    return card[0]+"<br />"+suitHTML[card[1]][0];
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