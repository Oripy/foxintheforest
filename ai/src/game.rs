use pyo3::types::{PyDict, PyList};

use std::fmt;
use std::collections::HashMap;

use crate::player::Player;
use crate::card::Card;
use crate::play::Play;

pub struct Game {
    pub plays: Vec<Play>,
    pub first_player: Option<Player>,
    pub init_draw_deck: Vec<Option<Card>>,
    pub init_trump_card: Option<Card>,
    pub init_hands: HashMap<Player, Vec<Option<Card>>>,
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

        let plays_strings: Vec<String> = self.plays.clone().into_iter().map(|c| format!("{}", c)).collect();
        let plays_string = plays_strings.join(" ");

        write!(f, "first player: {}\n\
                init_trump_card: {}\n\
                init_draw_deck: {:?}\n\
                Hands: P0: {:?}, P1: {:?}\n\
                Plays: {:?}", 
                self.first_player.as_ref().unwrap(),
                self.init_trump_card.as_ref().unwrap_or(&Card {rank: None, suit: None}),
                init_draw_deck_string,
                init_hand_p0_string,
                init_hand_p1_string,
                plays_string,
            )
    }
}

fn card_stack_from_python(list: &PyList) -> Vec<Option<Card>> {
    let mut stack = Vec::new();
    for i in 0..list.len() {
        let card: &PyList = list[i].extract().unwrap();
        stack.push(Some(Card::new_from_python(card)));
    }
    stack
}

fn play_list_from_python(list: &PyList) -> Vec<Play> {
    let mut play_list = Vec::new();
    for item in list.iter() {
        let play: &PyList = item.extract().unwrap();
        let player_python = play[0].extract::<i8>().unwrap();
        let mut player: Option<Player> = None;
        match player_python {
            0 => player = Some(Player::P0),
            1 => player = Some(Player::P1),
            _ => (),
        }
        let cur_play = Play {
            player: player.unwrap(),
            card: Some(Card::new_from_python(play[1].extract().unwrap())).unwrap_or_default(),
        };
        play_list.push(cur_play);
    }
    play_list
}

impl Game {
    pub fn new_from_python(dict: &PyDict) -> Game {
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
                    game.plays = play_list_from_python(value.extract::<&PyList>().unwrap());
                }
                "first_player" => {
                    let player = value.extract::<i8>().unwrap();
                    match player {
                        0 => game.first_player = Some(Player::P0),
                        1 => game.first_player = Some(Player::P1),
                        _ => (),
                    }
                }
                "init_draw_deck" => {
                    game.init_draw_deck = card_stack_from_python(value.extract::<&PyList>().unwrap());
                }
                "init_trump_card" => {
                    game.init_trump_card = Some(Card::new_from_python(value.extract().unwrap()));
                }
                "init_hands" => {
                    let init_hands = value.extract::<&PyList>().unwrap();
                    game.init_hands.insert(Player::P0, card_stack_from_python(init_hands[0].extract::<&PyList>().unwrap()));
                    game.init_hands.insert(Player::P1, card_stack_from_python(init_hands[1].extract::<&PyList>().unwrap()));
                }
                _ => {}
            }
        }
        game
    }
}