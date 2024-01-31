use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::{cmp, fmt};
use std::collections::HashMap;

#[derive(Clone, Debug, Ord, Eq, PartialOrd, PartialEq)]
enum Suit {
    H,
    S,
    C,
}

impl fmt::Display for Suit {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Suit::H => write!(f, "♥"),
            Suit::S => write!(f, "♠"),
            Suit::C => write!(f, "♣"),
        }
    }
}

#[derive(Clone, Hash, PartialEq, Eq)]
#[pyclass]
enum Player {
    P0,
    P1,
}

impl fmt::Display for Player {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Player::P0 => write!(f, "P0"),
            Player::P1 => write!(f, "P1"),
        }
    }
}

#[derive(Clone, Debug, Ord, PartialEq, Eq)]
#[pyclass]
struct Card {
    rank: Option<i8>,
    suit: Option<Suit>,
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let suit_display = format!("{}", self.suit.as_ref().unwrap());
        write!(f, "[{}{}]", self.rank.unwrap_or(0), suit_display)
    }
}

impl PartialOrd for Card {
    fn partial_cmp(&self, other: &Card) -> Option<cmp::Ordering> {
        if self.suit == other.suit {
            Some(self.rank.cmp(&other.rank))
        } else {
            Some(self.suit.cmp(&other.suit))
        }
    }
}

#[derive(Clone)]
struct Play {
    player: Player,
    card: Card,
}

struct Game {
    plays: Vec<Play>,
    first_player: Option<Player>,
    init_draw_deck: Vec<Option<Card>>,
    init_trump_card: Option<Card>,
    init_hands: HashMap<Player, Vec<Option<Card>>>,
}

impl fmt::Display for Game {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let mut init_draw_deck_copy = self.init_draw_deck.clone();
        init_draw_deck_copy.sort();
        let init_draw_deck_strings: Vec<String> = init_draw_deck_copy.into_iter().map(|c| format!("{}", c.unwrap())).collect();
        let init_draw_deck_string = init_draw_deck_strings.join(" ");

        let mut init_hand_p0_copy = self.init_hands[&Player::P0].clone();
        init_hand_p0_copy.sort();
        let init_hand_p0_strings: Vec<String> = init_hand_p0_copy.into_iter().map(|c| format!("{}", c.unwrap())).collect();
        let init_hand_p0_string = init_hand_p0_strings.join(" ");

        let mut init_hand_p1_copy = self.init_hands[&Player::P1].clone();
        init_hand_p1_copy.sort();
        let init_hand_p1_strings: Vec<String> = init_hand_p1_copy.into_iter().map(|c| format!("{}", c.unwrap())).collect();
        let init_hand_p1_string = init_hand_p1_strings.join(" ");

        let plays_strings: Vec<String> = self.plays.clone().into_iter().map(|c| format!("{}:{}", c.player, c.card)).collect();
        let plays_string = plays_strings.join(" ");

        write!(f, "first player: {}, init_trump_card: {}, init_draw_deck: {:?}, Hands: P0: {:?}, P1: {:?}, Plays: {:?}", 
                self.first_player.as_ref().unwrap(),
                self.init_trump_card.as_ref().unwrap_or(&Card {rank: None, suit: None}),
                init_draw_deck_string,
                init_hand_p0_string,
                init_hand_p1_string,
                plays_string,
            )
    }
}

// #[pyfunction]
fn card_from_python(list: &PyList) -> Option<Card> {
    let mut card = Card { rank: None, suit: None };
    for n in 0..2 {
        match n {
            0 => {
                let rank = list[0].extract::<i8>().ok()?;
                card.rank = Some(rank);
            }
            1 => {
                let suit = list[1].extract::<String>().ok()?;
                match suit.as_str() {
                    "h"=>card.suit = Some(Suit::H),
                    "s"=>card.suit = Some(Suit::S),
                    "c"=>card.suit = Some(Suit::C),
                    _=> {}
                }
            }
            _ => {}
        }
    }
    Some(card)
}

fn card_stack_from_python(list: &PyList) -> Option<Vec<Option<Card>>> {
    let mut stack = Vec::new();
    for i in 0..list.len() {
        let card: &PyList = list[i].extract().ok()?;
        stack.push(card_from_python(card));
    }
    Some(stack)
}

fn play_list_from_python(list: &PyList) -> Option<Vec<Play>> {
    let mut play_list = Vec::new();
    for item in list.iter() {
        let play: &PyList = item.extract().ok()?;
        let player_python = play[0].extract::<i8>().ok()?;
        let mut player: Option<Player> = None;
        match player_python {
            0 => player = Some(Player::P0),
            1 => player = Some(Player::P1),
            _ => (),
        }
        let cur_play = Play {
            player: player?,
            card: card_from_python(play[1].extract().ok()?).unwrap_or(Card {rank: None, suit: None}),
        };
        play_list.push(cur_play);
    }
    Some(play_list)
}

#[pyfunction]
fn game_from_python(dict: &PyDict) -> PyResult<String> {
    let mut game = Game {
        plays: Vec::new(),
        first_player: None,
        init_draw_deck: Vec::new(),
        init_trump_card: None,
        init_hands: HashMap::new(),
    };
    for (key, value) in dict.iter() {
        match key.to_string().as_str() {
            "plays" => {
                game.plays = play_list_from_python(value.extract::<&PyList>()?).unwrap();
            }
            "first_player" => {
                let player = value.extract::<i8>()?;
                match player {
                    0 => game.first_player = Some(Player::P0),
                    1 => game.first_player = Some(Player::P1),
                    _ => (),
                }
            }
            "init_draw_deck" => {
                game.init_draw_deck = card_stack_from_python(value.extract::<&PyList>()?).unwrap_or(Vec::new());
            }
            "init_trump_card" => {
                game.init_trump_card = card_from_python(value.extract()?);
            }
            "init_hands" => {
                let init_hands = value.extract::<&PyList>()?;
                game.init_hands.insert(Player::P0, card_stack_from_python(init_hands[0].extract::<&PyList>()?).unwrap_or(Vec::new()));
                game.init_hands.insert(Player::P1, card_stack_from_python(init_hands[1].extract::<&PyList>()?).unwrap_or(Vec::new()));
            }
            _ => {}
        }
    }
    Ok(format!("{}", game))
}

#[pymodule]
fn ai(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(card_from_python, m)?)?;
    m.add_function(wrap_pyfunction!(game_from_python, m)?)?;
    Ok(())
}
