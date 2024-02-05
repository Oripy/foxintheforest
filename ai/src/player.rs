use pyo3::prelude::*;
use std::fmt;
use rand::{
    distributions::{Distribution, Standard},
    Rng,
};

#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq)]
#[pyclass]
pub enum Player {
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

impl Player {
    pub fn next_player(self) -> Player {
        if self == Player::P0 {
            return Player::P1
        } else {
            return Player::P0
        }
    }
}

impl Distribution<Player> for Standard {
    fn sample<R: Rng + ?Sized>(&self, rng: &mut R) -> Player {
        match rng.gen_range(0..=1) {
            0 => Player::P0,
            _ => Player::P1,
        }
    }
}