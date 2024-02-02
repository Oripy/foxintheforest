use std::fmt;

#[derive(Clone, Copy, Debug, Ord, Eq, PartialOrd, PartialEq)]
pub enum Suit {
    H,
    S,
    C,
}

impl fmt::Display for Suit {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Suit::H => write!(f, "♥"),
            Suit::S => write!(f, "♠"),
            Suit::C => write!(f, "♣"),
        }
    }
}