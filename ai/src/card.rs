use pyo3::prelude::*;
use pyo3::types::PyList;
use std::{cmp, fmt};

use crate::suit::Suit;

#[derive(Clone, Debug, Ord, PartialEq, Eq)]
#[pyclass]
pub struct Card {
    pub rank: Option<i8>,
    pub suit: Option<Suit>,
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let suit_display = format!("{}", self.suit.as_ref().unwrap());
        write!(f, "[{}{}]", self.rank.unwrap(), suit_display)
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
        let mut card = Card { rank: None, suit: None };
        for n in 0..2 {
            match n {
                0 => {
                    let rank = list[0].extract::<i8>().ok();
                    card.rank = rank;
                }
                1 => {
                    let suit = list[1].extract::<String>().ok();
                    match suit.unwrap().as_str() {
                        "h"=>card.suit = Some(Suit::H),
                        "s"=>card.suit = Some(Suit::S),
                        "c"=>card.suit = Some(Suit::C),
                        _=> {}
                    }
                }
                _ => {}
            }
        }
        card
    }
}