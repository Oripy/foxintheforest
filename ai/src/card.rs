use pyo3::prelude::*;
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