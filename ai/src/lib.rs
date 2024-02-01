use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;

mod suit;
mod card;
mod player;
mod play;
mod game;
use crate::suit::Suit;
use crate::card::Card;
use crate::player::Player;
use crate::play::Play;
use crate::game::Game;

#[pyfunction]
fn print_game_from_python(dict: &PyDict) -> PyResult<String> {
    Ok(format!("{}", Game::new_from_python(dict)))
}

#[pymodule]
fn ai(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(card_from_python, m)?)?;
    m.add_function(wrap_pyfunction!(print_game_from_python, m)?)?;
    Ok(())
}
