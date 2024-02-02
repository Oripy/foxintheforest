use std::fmt;

use crate::player::Player;
use crate::card::Card;

#[derive(Clone, Debug)]
pub struct Play {
    pub player: Player,
    pub card: Card,
}

impl fmt::Display for Play {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}:{}", self.player, self.card)
    }
}