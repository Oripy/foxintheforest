use pyo3::prelude::*;
use pyo3::types::PyList;
use std::{cmp, fmt};

use crate::suit::Suit;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
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

impl Ord for Card {
    fn cmp(&self, other: &Card) -> cmp::Ordering {
        if self.suit == other.suit {
            self.rank.cmp(&other.rank)
        } else {
            self.suit.cmp(&other.suit)
        }
    }
}

impl PartialOrd for Card {
    fn partial_cmp(&self, other: &Card) -> Option<cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Card {
    pub fn new_from_python(list: &PyList) -> Card {
        let rank = list[0].extract::<i8>().expect("Invalid rank provided.");
        let suit_python = list[1].extract::<String>().ok();
        let suit = match suit_python.expect("Invalid suit provided.").as_str() {
            "h"=> Suit::H,
            "s"=> Suit::S,
            "c"=> Suit::C,
            _ => panic!("Invalid suit provided.")
        };
        Card {rank, suit}
    }
}