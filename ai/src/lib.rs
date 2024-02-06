use std::collections::HashMap;
use rand::prelude::*;

use pyo3::prelude::*;
use pyo3::types::PyDict;

mod suit;
mod card;
mod player;
mod play;
mod game;
mod state;
use crate::game::Game;
use crate::state::State;
use crate::player::Player;

#[pyfunction]
fn print_game_from_python(dict: &PyDict) -> PyResult<String> {
    Ok(format!("{}", Game::new_from_python(dict)))
}

#[pyfunction]
fn print_state_from_python_game(dict: &PyDict) -> PyResult<String> {
    let game = Game::new_from_python(dict);
    Ok(format!("{}", State::new(&game).ok().unwrap()))
}

#[pyfunction]
fn print_allowed_from_python_game(dict: &PyDict) -> PyResult<String> {
    let game = Game::new_from_python(dict);
    let state = State::new(&game).ok().unwrap();
    Ok(format!("{:?}", state.list_allowed()))
}

#[pyfunction]
fn play_game() -> PyResult<String> {
    let game = Game::new();
    let mut state = State::new(&game).ok().unwrap();
    while state.score == HashMap::from([(Player::P0, 0), (Player::P1, 0)]) {
        let mut allowed = state.list_allowed();
        allowed.shuffle(&mut rand::thread_rng());
        state.apply_play(&allowed[0]).ok();
    }
    Ok(format!("{}", state))
}

#[pymodule]
fn ai(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(print_game_from_python, m)?)?;
    m.add_function(wrap_pyfunction!(print_state_from_python_game, m)?)?;
    m.add_function(wrap_pyfunction!(print_allowed_from_python_game, m)?)?;
    m.add_function(wrap_pyfunction!(play_game, m)?)?;
    Ok(())
}
