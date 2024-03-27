use std::borrow::BorrowMut;
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
mod node;
use crate::game::Game;
use crate::state::State;
use crate::player::Player;
use crate::node::Node;

#[pyfunction]
fn print_game_from_python(dict: &PyDict) -> PyResult<String> {
    Ok(format!("{}", Game::new_from_python(dict)))
}

#[pyfunction]
fn print_state_from_python_game(dict: &PyDict) -> PyResult<String> {
    let game = Game::new_from_python(dict);
    Ok(format!("{}", State::from(&game).ok().unwrap()))
}

#[pyfunction]
fn print_allowed_from_python_game(dict: &PyDict) -> PyResult<String> {
    let game = Game::new_from_python(dict);
    let state = State::from(&game).ok().unwrap();
    Ok(format!("{:?}", state.list_allowed()))
}

#[pyfunction]
fn play_game() -> PyResult<String> {
    let game = Game::new();
    let mut state = State::from(&game).ok().unwrap();
    while state.score == HashMap::from([(Player::P0, 0), (Player::P1, 0)]) {
        let mut allowed = state.list_allowed();
        allowed.shuffle(&mut rand::thread_rng());
        state.apply_play(&allowed[0]).ok();
    }
    Ok(format!("{}", state))
}

#[pyfunction]
fn generate_plausible_states() -> PyResult<String> {
    let game = Game::new();
    let mut state = State::from(&game).ok().unwrap();
    println!("-- Initial state --");
    println!("{}", state);
    println!("-- Generated state --");
    while state.score == HashMap::from([(Player::P0, 0), (Player::P1, 0)]) {
        let mut allowed = state.list_allowed();
        allowed.shuffle(&mut rand::thread_rng());
        state.apply_play(&allowed[0]).ok();
        println!("-- new turn --");
        println!("-True state-");
        println!("{}", state);
        for i in 0..2 {
            println!("-Rand state {}-", i);
            let new_state = state.get_plausible_state(Player::P0);
            println!("{}", new_state);
        }
    }
    Ok(String::from("-- Done --"))
}

// #[pyfunction]
// fn test_node() -> PyResult<String> {
//     let game = Game::new();
//     let root_id = Node::new();
//     let guard = NODE_LIST.lock().unwrap();
//     let root = &guard[root_id];
//     let state = State::from(&game).unwrap();
//     for i in 0..100 {
//         let allowed = state.list_allowed();
//         if !root.get_untried(allowed).is_empty() {
//             let selected = &root.ucb_select_child(allowed).unwrap();
//         }
//     }

//     Ok(String::from("-- Done --"))
// }

#[pymodule]
fn ai(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(print_game_from_python, m)?)?;
    m.add_function(wrap_pyfunction!(print_state_from_python_game, m)?)?;
    m.add_function(wrap_pyfunction!(print_allowed_from_python_game, m)?)?;
    m.add_function(wrap_pyfunction!(play_game, m)?)?;
    m.add_function(wrap_pyfunction!(generate_plausible_states, m)?)?;
    // m.add_function(wrap_pyfunction!(test_node, m)?)?;
    Ok(())
}
