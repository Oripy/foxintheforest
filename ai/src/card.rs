use pyo3::prelude::*;
use pyo3::types::PyList;
use std::{cmp, fmt};

use crate::suit::Suit;

#[derive(Clone, Copy, Debug, Ord, PartialEq, Eq)]
#[pyclass]
pub struct Card {
    pub rank: i8,
    pub suit: Suit,
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let suit_display = format!("{}", self.suit);
        write!(f, "[{}{}]", self.rank, suit_display)
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

impl Card {
    pub fn new_from_python(list: &PyList) -> Card {
        let mut rank: i8 = 0;
        let mut suit = Suit::C;
        // let mut card = Card { rank: None, suit: None };
        for n in 0..2 {
            match n {
                0 => {
                    rank = list[0].extract::<i8>().unwrap();
                }
                1 => {
                    let suit_python = list[1].extract::<String>().ok();
                    match suit_python.unwrap().as_str() {
                        "h"=> suit = Suit::H,
                        "s"=> suit = Suit::S,
                        "c"=> suit = Suit::C,
                        _=> {},
                    }
                }
                _ => {}
            }
        }
        Card {rank, suit}
    }
}