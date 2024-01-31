use pyo3::prelude::*;
use std::fmt;

#[derive(Clone, Hash, PartialEq, Eq)]
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
