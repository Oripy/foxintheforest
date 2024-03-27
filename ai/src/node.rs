use std::fmt;
use std::rc::Rc;

use crate::Game;
use crate::State;
use crate::Player;
use crate::play::Play;

const EXPLORATION: f32 = 0.7;

use std::sync::{Arc, Mutex};

pub struct Node {
    pub play: Option<Play>,
    pub availability: usize,
    pub visits: usize,
    pub reward: f32,
    pub children: Mutex<Vec<Arc<Node>>>,
    pub parent: Option<Arc<Node>>,
}

impl Node {
    pub fn new() -> Self {
        Node {
            play: None,
            availability: 0,
            visits: 0,
            reward: 0.0,
            children: Mutex::new(vec![]),
            parent: None,
        }
    }

    // impl fmt::Display for Node {
//     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
//         let mut node_play_string = String::from("Root");
//         let mut turn_count = 0;
//         let state = self.state.clone();
//         let last_play = state.plays.last();
//         if last_play.is_some() {
//             node_play_string = format!("{:}", state.plays.last().unwrap());
//         }
//         turn_count = state.discards[&Player::P0].len() + state.discards[&Player::P1].len();
//         if state.trick[&Player::P0].is_some() {
//             turn_count += 1;
//         }
//         if state.trick[&Player::P1].is_some() {
//             turn_count += 1;
//         }
//         write!(f, "Node {}, Turn {}, visits {}, reward {}, avail. {}", node_play_string, turn_count, self.visits, self.reward, self.availability)
//     }
// }

    pub fn add_child(&self, child: Arc<Node>) {
        let mut children = self.children.lock().unwrap();
        children.push(child.clone());
        child.parent = Some(Arc::clone(self));
    }

    pub fn get_children(&self) -> Vec<Arc<Node>> {
        let children = self.children.lock().unwrap();
        children.clone() // Clone the borrowed vector for safe usage outside the lock
    }

    fn update(mut self, reward: f32) {
        self.visits += 1;
        self.reward += reward;
    }

    // pub fn get_untried(&self, allowed: Vec<Play>) -> Vec<Play> {
    //     let mut tried: Vec<Play> = Vec::new();
    //     for child in &self.children {
    //         tried.push(child.play.unwrap());
    //     }
    //     let mut untried: Vec<Play> = Vec::new();
    //     for play in &allowed {
    //         if !tried.contains(play) {
    //             untried.push(*play);
    //         }
    //     }
    //     untried
    // }

    // fn get_ucb(&self) -> f32 {
    //     self.reward / (self.visits as f32) + EXPLORATION * ((self.availability as f32).ln() / self.visits as f32).sqrt()
    // }

    // pub fn ucb_select_child(self, allowed: Vec<Play>) -> Option<Rc<Node>> {
    //     let mut max_ucb = 0.0;
    //     let mut selected = None;
    //     for child in self.children {    
    //         let play = &child.play.unwrap();
    //         if allowed.contains(play) {
    //             let ucb = child.get_ucb();
    //             if ucb > max_ucb {
    //                 max_ucb = ucb;
    //                 selected = Some(child);
    //             }
    //         }
    //     }
    //     selected
    // }
}