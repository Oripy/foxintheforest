let step = 0;
let game_id = undefined;

document.getElementById("new").addEventListener("click", event => {
  fetch(`/play`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify({play: "new_game"}),
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
      step = 0;
      game_id = res.id;
      updateState(res);
    });
  });
});

function updateState(res) {
  state = res.states[step];

  if (step != 0) {
    card_played = res.steps[step-1][1];
  } else {
    card_played = [undefined, undefined];
  }
  let opponenthand = document.getElementById("opponenthand");
  while (opponenthand.firstChild) {
    opponenthand.removeChild(opponenthand.firstChild);
  }
  for (let i = 0; i < state.hands[1].length; i++) {
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
  if (state.trick[1] != null) {
    ot.innerHTML = cardHTML(state.trick[1]);
    ot.className = "playingcard";
    ot.classList.add(suitHTML[state.trick[1][1]][1]);
    if ((state.trick[1][0] == card_played[0]) && (state.trick[1][1] == card_played[1])) {
      ot.classList.add("highlight");
    }
  } else {
    ot.innerHTML = cardHTML("empty");
    ot.className = "playingcard empty";
  }

  let pt = document.getElementById("pt");
  if (state.trick[0] != null) {
    pt.innerHTML = cardHTML(state.trick[0]);
    pt.className = "playingcard";
    pt.classList.add(suitHTML[state.trick[0][1]][1]);
    if ((state.trick[0][0] == card_played[0]) && (state.trick[0][1] == card_played[1])) {
      pt.classList.add("highlight");
    }
  } else {
    pt.innerHTML = cardHTML("empty");
    pt.className = "playingcard empty";
  }

  let pscore = document.getElementById("playerscore");
  pscore.innerHTML = Math.floor(state.discards[0].length/2);
  let oscore = document.getElementById("opponentscore");
  oscore.innerHTML = Math.floor(state.discards[1].length/2);

  let plasttrick = document.getElementById("plasttrick");
  let pdiscardlength = state.discards[0].length;
  while (plasttrick.firstChild) {
    plasttrick.removeChild(plasttrick.firstChild);
  }
  if (pdiscardlength >= 2) { 
    for (let i = 0; i < 2; i++) {
      let card = document.createElement("div");
      cardvalue = state.discards[0][pdiscardlength-2+i];
      card.innerHTML = cardHTML(cardvalue);
      card.className = "playingcard";
      card.classList.add(suitHTML[cardvalue[1]][1]);
      if ((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) {
        card.classList.add("highlight");
      }
      plasttrick.appendChild(card);
    }
  }

  let olasttrick = document.getElementById("olasttrick");
  let odiscardlength = state.discards[1].length;
  while (olasttrick.firstChild) {
    olasttrick.removeChild(olasttrick.firstChild);
  }
  if (odiscardlength >= 2) {
    for (let i = 0; i < 2; i++) {
      let card = document.createElement("div");
      cardvalue = state.discards[1][odiscardlength-2+i];
      card.innerHTML = cardHTML(cardvalue);
      card.className = "playingcard";
      card.classList.add(suitHTML[cardvalue[1]][1]);
      if ((cardvalue[0] == card_played[0]) && (cardvalue[1] == card_played[1])) {
        card.classList.add("highlight");
      }
      olasttrick.appendChild(card);
    }
  }

  let playerhand = document.getElementById("playerhand");
  while (playerhand.firstChild) {
    playerhand.removeChild(playerhand.firstChild);
  }
  let hand = state.hands[0].sort((a, b) => {
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
    if ((hand[i][0] == card_played[0]) && (hand[i][1] == card_played[1])) {
      card.classList.add("highlight");
    }
    card.id = hand[i][0] + hand[i][1];
    playerhand.appendChild(card);
    card.addEventListener("click", event => {
      let card_id = event.target.id;
      fetch(`/play`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({id: game_id, play: card_id, player: 0}),
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
    });
  }
  if (state.current_player == 1) {
    setTimeout(() => {fetch(`/play`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({id:game_id, play: null, player: 1}),
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
    }, 1000);
  }
  step++;
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