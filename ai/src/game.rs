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
