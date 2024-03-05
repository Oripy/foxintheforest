use std::fmt;
use std::collections::HashMap;

use rand::seq::SliceRandom;

use crate::player::Player;
use crate::card::Card;
use crate::play::{InvalidPlay, Play};
use crate::game::Game;

#[derive(Clone, Copy, PartialEq)]
enum NextPlayType {
    Normal,
    Trump,
    Draw,
}

#[derive(Clone)]
pub struct State {
    pub plays: Vec<Play>,
    pub trick: HashMap<Player, Option<Card>>,
    current_player: Player,
    leading_player: Player,
    pub score: HashMap<Player, usize>,
    pub discards: HashMap<Player, Vec<Card>>,
    hands: HashMap<Player, Vec<Card>>,
    trump_card: Option<Card>,
    draw_deck: Vec<Card>,
    next_play_type: NextPlayType,
    private_discards: HashMap<Player, Vec<Card>>,
}

impl fmt::Display for State {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let mut draw_deck_copy = self.draw_deck.clone();
        draw_deck_copy.sort();
        let draw_deck_strings: Vec<String> = draw_deck_copy.into_iter().map(|c| format!("{}", c)).collect();
        let draw_deck_string = draw_deck_strings.join(" ");

        let mut hand_p0_copy = self.hands[&Player::P0].clone();
        hand_p0_copy.sort();
        let hand_p0_strings: Vec<String> = hand_p0_copy.into_iter().map(|c| format!("{}", c)).collect();
        let hand_p0_string = hand_p0_strings.join(" ");

        let mut hand_p1_copy = self.hands[&Player::P1].clone();
        hand_p1_copy.sort();
        let hand_p1_strings: Vec<String> = hand_p1_copy.into_iter().map(|c| format!("{}", c)).collect();
        let hand_p1_string = hand_p1_strings.join(" ");

        let plays_strings: Vec<String> = self.plays.clone().into_iter().map(|c| format!("{}", c)).collect();
        let plays_string = plays_strings.join(" ");

        let trump_card: String = match self.trump_card {
            None => String::from("--"),
            _ => format!("{:?}", self.trump_card),
        };

        write!(f, "current player: {}\n\
                   trump card: {}\n\
                   draw deck: {}\n\
                   hands: P0: {:?}, P1: {:?}\n\
                   score: {:?}\n\
                   plays: {:?}", 
                   self.current_player,
                   trump_card,
                   draw_deck_string,
                   hand_p0_string,
                   hand_p1_string,
                   self.score,
                   plays_string,)
    }
}

impl State {
    pub fn from(game: &Game) -> Result<State, InvalidPlay> {
        let mut state = State {
            plays: Vec::new(),
            trick: HashMap::from([(Player::P0, None), (Player::P1, None)]),
            current_player: game.first_player,
            leading_player: game.first_player,
            score: HashMap::from([(Player::P0, 0), (Player::P1, 0)]),
            discards: HashMap::from([(Player::P0, Vec::new()), (Player::P1, Vec::new())]),
            hands: game.init_hands.clone(),
            trump_card: Some(game.init_trump_card),
            draw_deck: game.init_draw_deck.clone(),
            next_play_type: NextPlayType::Normal,
            private_discards: HashMap::from([(Player::P0, Vec::new()), (Player::P1, Vec::new())]),
        };
        for p in &game.plays {
            match state.apply_play(p) {
                Ok(_) => (),
                Err(e) => {
                    println!("{}", state);
                    return Err(e);
                },
            };
        };
        Ok(state)
    }

    pub fn calculate_score(&mut self) {
        self.score = HashMap::from([(Player::P0, 0), (Player::P1, 0)]);
        let mut tricks_won: HashMap<Player, usize> = Default::default();
        for player in [Player::P0, Player::P1] {
            for card in &self.discards[&player] {
                if card.rank == 7 {
                    *self.score.entry(player).or_default() += 1;
                }
            }
            tricks_won.insert(player, self.discards[&player].len()/2);
        }
    
        if tricks_won[&Player::P0] + tricks_won[&Player::P1] == 13 {
            for player in [Player::P0, Player::P1] {
                match tricks_won[&player] {
                    0..=3 => *self.score.entry(player).or_default() += 6, // Humble
                    4 => *self.score.entry(player).or_default() += 1, // Defeated
                    5 => *self.score.entry(player).or_default() += 2, // Defeated
                    6 => *self.score.entry(player).or_default() += 3, // Defeated
                    7..=9 => *self.score.entry(player).or_default() += 6, // Victorious
                    _ => (), // Greedy
                }
            }
        }
    }

    pub fn apply_play(&mut self, play: &Play) -> Result<(), InvalidPlay> {
        if play.player != self.current_player {
            return Err(InvalidPlay);
        }
        if !self.hands[&self.current_player].contains(&play.card) {
            return Err(InvalidPlay);
        }
        match &self.next_play_type {
            NextPlayType::Normal => {
                let index = self.hands[&self.current_player].iter().position(|&c| c == play.card).ok_or(InvalidPlay)?;
                self.trick.insert(self.current_player, Some(self.hands.get_mut(&self.current_player).unwrap().remove(index)));
                match &play.card.rank {
                    3 => {
                        self.next_play_type = NextPlayType::Trump;
                        self.hands.get_mut(&self.current_player).unwrap().push(self.trump_card.ok_or(InvalidPlay)?);
                        self.trump_card = None;
                    },
                    5 => {
                        self.next_play_type = NextPlayType::Draw;
                        self.hands.get_mut(&self.current_player).unwrap().push(self.draw_deck.remove(0));  
                    },
                    _ => (),
                }
            },
            NextPlayType::Trump => {
                let index = self.hands[&self.current_player].iter().position(|&c| c == play.card).ok_or(InvalidPlay)?;
                self.trump_card = Some(self.hands.get_mut(&self.current_player).unwrap().remove(index));
                self.next_play_type = NextPlayType::Normal;
            },
            NextPlayType::Draw => {
                let index = self.hands[&self.current_player].iter().position(|&c| c == play.card).ok_or(InvalidPlay)?;
                self.private_discards.get_mut(&self.current_player).unwrap().push(self.hands.get_mut(&self.current_player).unwrap().remove(index));
                self.next_play_type = NextPlayType::Normal;
            },
        }
        if self.next_play_type == NextPlayType::Normal {
            if self.trick[&Player::P0].is_some() && self.trick[&Player::P1].is_some() {
                let winner: Player;
                let mut p0suit = self.trick[&Player::P0].unwrap().suit;
                let p0rank = self.trick[&Player::P0].unwrap().rank;
                let mut p1suit = self.trick[&Player::P1].unwrap().suit;
                let p1rank = self.trick[&Player::P1].unwrap().rank;
                let trump_suit = self.trump_card.unwrap().suit;
                if p0rank == 9 && p1rank != 9 {
                    p0suit = trump_suit;
                }
                if p1rank == 9 && p0rank != 9 {
                    p1suit = trump_suit;
                }
                if p0suit == p1suit {
                    if p0rank > p1rank {
                        winner = Player::P0;
                    } else {
                        winner = Player::P1; 
                    }
                } else if p0suit == trump_suit {
                    winner = Player::P0;
                } else if p1suit == trump_suit {
                    winner = Player::P1;
                } else {
                    winner = self.leading_player;
                }
                self.current_player = winner;
                if winner == Player::P0 && p1rank == 1 {
                    self.current_player = Player::P1;
                } else if winner == Player::P1 && p0rank == 1 {
                    self.current_player = Player::P0;
                }
                self.leading_player = self.current_player;
                self.discards.get_mut(&winner).unwrap().push(self.trick[&Player::P0].unwrap());
                self.discards.get_mut(&winner).unwrap().push(self.trick[&Player::P1].unwrap());
                self.trick = HashMap::from([(Player::P0, None), (Player::P1, None)]);
            } else {
                self.current_player = self.current_player.next_player()
            }
        }
        self.plays.push(*play);
        if self.hands[&Player::P0].is_empty() && self.hands[&Player::P1].is_empty() {
            self.calculate_score();
        }
        Ok(())
    }

    pub fn list_allowed(&self) -> Vec<Play> {
        if self.trick[&self.current_player].is_some() || self.trick[&self.current_player.next_player()].is_none() {
            return self.hands[&self.current_player].clone().into_iter().map(|x| Play {player: self.current_player, card: x}).collect();
        }
        let mut allowed = Vec::new();
        let other_card = &self.trick[&self.current_player.next_player()].unwrap();
        
        let mut best_card: Option<Card> = None;
        for card in &self.hands[&self.current_player] {
            if other_card.suit == card.suit {
                if other_card.rank == 11 {
                    if card.rank == 1 {
                        allowed.push(Play {player: self.current_player, card: *card});
                    } else if card.rank > best_card.unwrap().rank {
                        best_card = Some(*card);
                    }
                } else {
                    allowed.push(Play {player: self.current_player, card: *card});
                }
            }
        }
        if let Some(best_card_real) = best_card {
            allowed.push(Play {player: self.current_player, card: best_card_real});
        }
        if allowed.is_empty() {
            return self.hands[&self.current_player].clone().into_iter().map(|x| Play {player: self.current_player, card: x}).collect();
        }
        allowed
    }

    pub fn get_plausible_state(&self, player: Player) -> State {
        let mut remaining_cards: Vec<Card> = Vec::new();
        for card in &self.hands[&player.next_player()] {
            remaining_cards.push(*card);
        }
        for card in &self.draw_deck {
            remaining_cards.push(*card);
        }
        for card in &self.private_discards[&player.next_player()] {
            remaining_cards.push(*card);
        }
        remaining_cards.shuffle(&mut rand::thread_rng());
        let opponent_hand = remaining_cards.drain(0..self.hands[&player.next_player()].len()).collect();
        let draw_deck = remaining_cards.drain(0..self.draw_deck.len()).collect();
        let opponent_private_discard = remaining_cards.drain(0..self.private_discards[&player.next_player()].len()).collect();
        State {
            plays: self.plays.clone(),
            trick: self.trick.clone(),
            current_player: self.current_player,
            leading_player: self.leading_player,
            score: self.score.clone(),
            discards: self.discards.clone(),
            hands: HashMap::from([(player, self.hands[&player].clone()), (player.next_player(), opponent_hand)]),
            trump_card: self.trump_card,
            draw_deck,
            next_play_type: NextPlayType::Normal,
            private_discards: HashMap::from([(player, self.private_discards[&player].clone()), (player.next_player(), opponent_private_discard)]),
        }
    }
}