use pyo3::types::{PyDict, PyList};

use std::fmt;
use std::collections::HashMap;

use rand::prelude::*;

use crate::player::Player;
use crate::card::Card;
use crate::play::Play;
use crate::suit::Suit;

pub struct Game {
    pub plays: Vec<Play>,
    pub first_player: Player,
    pub init_draw_deck: Vec<Card>,
    pub init_trump_card: Card,
    pub init_hands: HashMap<Player, Vec<Card>>,
}

impl fmt::Display for Game {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let mut init_draw_deck_copy = self.init_draw_deck.clone();
        init_draw_deck_copy.sort();
        let init_draw_deck_strings: Vec<String> = init_draw_deck_copy.into_iter().map(|c| format!("{}", c)).collect();
        let init_draw_deck_string = init_draw_deck_strings.join(" ");

        let mut init_hand_p0_copy = self.init_hands[&Player::P0].clone();
        init_hand_p0_copy.sort();
        let init_hand_p0_strings: Vec<String> = init_hand_p0_copy.into_iter().map(|c| format!("{}", c)).collect();
        let init_hand_p0_string = init_hand_p0_strings.join(" ");

        let mut init_hand_p1_copy = self.init_hands[&Player::P1].clone();
        init_hand_p1_copy.sort();
        let init_hand_p1_strings: Vec<String> = init_hand_p1_copy.into_iter().map(|c| format!("{}", c)).collect();
        let init_hand_p1_string = init_hand_p1_strings.join(" ");

        let plays_strings: Vec<String> = self.plays.clone().into_iter().map(|c| format!("{}", c)).collect();
        let plays_string = plays_strings.join(" ");

        write!(f, "first player: {}\n\
                init_trump_card: {}\n\
                init_draw_deck: {:?}\n\
                Hands: P0: {:?}, P1: {:?}\n\
                Plays: {:?}", 
                self.first_player,
                self.init_trump_card,
                init_draw_deck_string,
                init_hand_p0_string,
                init_hand_p1_string,
                plays_string,
            )
    }
}

fn card_stack_from_python(list: &PyList) -> Vec<Card> {
    let mut stack = Vec::new();
    for i in 0..list.len() {
        let card: &PyList = list[i].extract().expect("Invalid card.");
        stack.push(Card::new_from_python(card));
    }
    stack
}

fn play_list_from_python(list: &PyList) -> Vec<Play> {
    let mut play_list = Vec::new();
    for item in list.iter() {
        let play: &PyList = item.extract().expect("Invalid play.");
        let player = match play[0].extract::<i8>().expect("Invalid player.") {
            0 => Player::P0,
            1 => Player::P1,
            _ => panic!("Invalid player."),
        };
        play_list.push(Play {
            player,
            card: Card::new_from_python(play[1].extract().expect("Invalid python input.")),
        });
    }
    play_list
}

impl Game {
    pub fn new() -> Game {
        let mut deck: Vec<Card> = Vec::new();
        for rank in 1..=11 {
            for suit in [Suit::H, Suit::S, Suit::C] {
                deck.push(Card {rank, suit})
            }
        }
        deck.shuffle(&mut rand::thread_rng());
        let first_player: Player = rand::random();
        Game {
            plays: Vec::new(),
            first_player,
            init_draw_deck: deck.drain(0..6).collect(),
            init_trump_card: deck.drain(0..1).collect::<Vec<_>>()[0],
            init_hands: HashMap::from([(Player::P0, deck.drain(0..13).collect()), (Player::P1, deck.drain(0..13).collect())]),
        }
    }

    pub fn new_from_python(dict: &PyDict) -> Game {
        let mut plays = Vec::new();
        let mut first_player: Option<Player> = None;
        let mut init_draw_deck = Vec::new();
        let mut init_trump_card: Option<Card> = None;
        let mut init_hands: HashMap<Player, Vec<Card>> = HashMap::new();
        for (key, value) in dict.iter() {
            match key.to_string().as_str() {
                "plays" => {
                    plays = play_list_from_python(value.extract::<&PyList>().expect("Can't read plays."));
                }
                "first_player" => {
                    let player = value.extract::<i8>().expect("Can't read player.");
                    match player {
                        0 => first_player = Some(Player::P0),
                        _ => first_player = Some(Player::P1),
                    }
                }
                "init_draw_deck" => {
                    init_draw_deck = card_stack_from_python(value.extract::<&PyList>().expect("Can't read card."));
                }
                "init_trump_card" => {
                    init_trump_card = Some(Card::new_from_python(value.extract().expect("Can't read init_trump_card.")));
                }
                "init_hands" => {
                    let init_hands_python = value.extract::<&PyList>().expect("Invalid python input.");
                    init_hands.insert(Player::P0, card_stack_from_python(init_hands_python[0].extract::<&PyList>().expect("Can't read card.")));
                    init_hands.insert(Player::P1, card_stack_from_python(init_hands_python[1].extract::<&PyList>().expect("Can't read card.")));
                }
                _ => {}
            }
        }
        Game {
            plays,
            first_player: first_player.expect("No \"first_player\" in input python dict"),
            init_draw_deck,
            init_trump_card: init_trump_card.expect("No \"init_trump_card\" in input python dict"),
            init_hands,
        }
    }
}