
use pyo3::prelude::*;

const K: f32 = 5.0;

#[pyfunction]
fn upper_confidence_bound(reward: f32, visits: f32, availability: f32) -> f32 {
    reward / visits + K * (availability.ln() / visits).sqrt()
}

#[derive(Clone, Copy)]
enum Color{Hearts, Spades, Clubs}

#[pyclass]
#[derive(Clone, Copy)]
struct Card {
    value: u8, 
    color: Color
}

// #[pymethods]
// impl Card {
//     #[getter]
//     fn get_value(&self) -> PyResult<u8> {
//         Ok(self.value)
//     }
//     #[setter]
//     fn set_value(&mut self, value: u8) -> PyResult<()> {
//         self.value = value;
//         Ok(())
//     }
//     #[getter]
//     fn get_color(&self) -> PyResult<Color> {
//         Ok(self.color)
//     }
//     #[setter]
//     fn set_color(&mut self, value: Color) -> PyResult<()> {
//         self.color = value;
//         Ok(())
//     }
// }

#[pyclass]
#[derive(Clone)]
struct Play{
    player: u8,
    card: Card
}

// #[pymethods]
// impl Play {
//     #[getter]
//     fn get_player(&self) -> PyResult<u8> {
//         Ok(self.player)
//     }
//     #[setter]
//     fn set_player(&mut self, value: u8) -> PyResult<()> {
//         self.player = value;
//         Ok(())
//     }
//     #[getter]
//     fn get_card(&self) -> PyResult<Card> {
//         Ok(self.card)
//     }
//     #[setter]
//     fn set_card(&mut self, value: Card) -> PyResult<()> {
//         self.card = value;
//         Ok(())
//     }
// }

#[pyclass]
#[derive(Clone)]
struct Node {
    play: Play,
    parent: Box<Node>,
    availability: usize,
    visits: usize,
    reward: usize,
    children: Vec<Play>,
    outcome_p0: [usize; 4]
}

#[pymethods]
impl Node {
    #[new]
    fn new(play: Play, parent: Node) -> Self {
        Node { play: play, parent: Box::new(parent), availability: 0, visits: 0, reward: 0, children: Vec::new(), outcome_p0: [0, 0, 0, 0] }
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyext_good_ai(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(upper_confidence_bound, m)?)?;
    m.add_class::<Node>()?;
    Ok(())
}