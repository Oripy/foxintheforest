use pyo3::prelude::*;
use pyo3::types::PyDict;

mod suit;
mod card;
mod player;
mod play;
mod game;
use crate::game::Game;

#[pyfunction]
fn print_game_from_python(dict: &PyDict) -> PyResult<String> {
    Ok(format!("{}", Game::new_from_python(dict)))
}

#[pymodule]
fn ai(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(print_game_from_python, m)?)?;
    Ok(())
}
