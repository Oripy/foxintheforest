use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;

mod suit;
mod card;
mod player;
mod play;
mod game;
use crate::suit::Suit;
use crate::card::Card;
use crate::player::Player;
use crate::play::Play;
use crate::game::Game;

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
