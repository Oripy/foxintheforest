import unittest
import foxy.foxintheforest as foxintheforest
import random

class TestBasicFunctions(unittest.TestCase):
    def test_other_player(self):
        self.assertEqual(foxintheforest.other_player(1), 0)
        self.assertEqual(foxintheforest.other_player(0), 1)
    
    def test_trick_winner(self):
        self.assertFalse(foxintheforest.trick_winner(0, [None, None], [1, "s"]))
        self.assertFalse(foxintheforest.trick_winner(0, [[1, "c"], None], [1, "s"]))
        self.assertFalse(foxintheforest.trick_winner(0, [None, [1, "c"]], [1, "s"]))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[4, "c"], [2, "c"]], [1, "s"]), (0, 0))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[2, "c"], [4, "c"]], [1, "s"]), (1, 1))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[4, "c"], [2, "s"]], [1, "s"]), (1, 1))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[4, "c"], [2, "h"]], [1, "s"]), (0, 0))
        self.assertTupleEqual(foxintheforest.trick_winner(1, [[4, "c"], [2, "h"]], [1, "s"]), (1, 1))

        self.assertTupleEqual(foxintheforest.trick_winner(0, [[1, "c"], [2, "c"]], [1, "s"]), (1, 0))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[2, "c"], [1, "c"]], [1, "s"]), (0, 1))
    
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[9, "c"], [11, "c"]], [1, "s"]), (0, 0))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[9, "s"], [11, "s"]], [1, "s"]), (1, 1))
        self.assertTupleEqual(foxintheforest.trick_winner(0, [[9, "c"], [9, "h"]], [1, "s"]), (0, 0))
    
    def test_decode_card(self):
        self.assertEqual(foxintheforest.decode_card("1s"), [1, "s"])
        self.assertEqual(foxintheforest.decode_card("10s"), [10, "s"])
        self.assertEqual(foxintheforest.decode_card("10s"), [10, "s"])
        self.assertFalse(foxintheforest.decode_card("a"))

class TestDeckManipulations(unittest.TestCase):
    def setUp(self):
        self.deck = [[1, "h"], [5, "s"], [11, "c"]]

    def test_pick_cards(self):
        self.assertListEqual(foxintheforest.pick_cards(self.deck, 2), [[1, "h"], [5, "s"]])
        self.assertListEqual(self.deck, [[11, "c"]])

class TestGameInit(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.game = foxintheforest.new_game()

    def test_new_game(self):
        self.assertEqual(len(self.game), 5)
        self.assertDictEqual(self.game, {
            'plays': [],
            'first_player': 1,
            'init_draw_deck': [[3, 'c'], [5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']],
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            })

    def test_copy_game(self):
        game_copy = foxintheforest.copy_game(self.game)
        self.assertDictEqual(game_copy, {
            'plays': [],
            'first_player': 1,
            'init_draw_deck': [[3, 'c'], [5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']],
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            })

    def test_get_game_state(self):
        state = foxintheforest.get_state_from_game(self.game)
        self.assertDictEqual(state, {
            'plays': [],
            'private_discards': [[], []],
            'trick': [None, None],
            'current_player': 1,
            'leading_player': 1,
            'score': [0, 0],
            'discards': [[], []],
            'hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                      [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'], [8, 's']],
                      [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                       [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]],
            'init_trump_card': [4, 's'],
            'trump_card': [4, 's'],
            'draw_deck': [[3, 'c'], [5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']]})
    
    def test_get_player_game(self):
        self.assertDictEqual(foxintheforest.get_player_game(self.game, 0), {
            'player': 0,
            'plays': [],
            'first_player': 1,
            'init_draw_deck': [[None, None]]*6,
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[None, None]]*13]
            }
        )
        self.assertDictEqual(foxintheforest.get_player_game(self.game, 1), {
            'player': 1,
            'plays': [],
            'first_player': 1,
            'init_draw_deck': [[None, None]]*6,
            'init_trump_card': [4, 's'],
            'init_hands': [[[None, None]]*13,
                           [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            }
        )

class TestPlay(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.game = foxintheforest.new_game()
        self.state = foxintheforest.get_state_from_game(self.game)
    
    def test_valid_step(self):
        self.assertFalse(foxintheforest.valid_step(self.state, [0, [3, 'h']])) # Wrong player playing
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [3, 'h']])) # Card not in hand
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [1, 'h']]))
        foxintheforest.apply_play(self.game, [1, [1, 'h']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [0, [9, 'c']])) # Wrong suit
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [2, 'h']]))
        foxintheforest.apply_play(self.game, [0, [2, 'h']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [0, [3, 'h']])) # Wrong player playing after 1 card played by opponent
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [5, 'c']]))
        foxintheforest.apply_play(self.game, [1, [5, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [0, [3, 'h']])) # Wrong player playing after 5 card played
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [1, 'h']])) # Card no longer in hand
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [3, 'c']]))
        foxintheforest.apply_play(self.game, [1, [3, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [9, 'c']]))
        foxintheforest.apply_play(self.game, [0, [9, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [11, 's']]))
        foxintheforest.apply_play(self.game, [0, [11, 's']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [3, 's']])) # Not highest card of suit and not 1 of suit after 11
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [1, 's']])) # 1 of suit after 11
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [10, 's']])) # highest card of suit after 11
        foxintheforest.apply_play(self.game, [1, [10, 's']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [3, 'h']]))
        foxintheforest.apply_play(self.game, [0, [3, 'h']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [7, 'h']])) # Wrong player playing after 3 card played
        self.assertFalse(foxintheforest.valid_step(self.state, [0, [2, 'h']])) # Card no longer in hand
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [6, 'c']]))
        foxintheforest.apply_play(self.game, [0, [6, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [2, 'c']])) # Wrong suit
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [7, 'h']]))
    
    def test_valid_step_card9(self):
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [9, 's']]))
        foxintheforest.apply_play(self.game, [1, [9, 's']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [11, 's']]))
        foxintheforest.apply_play(self.game, [0, [11, 's']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [2, 'c']])) # Wrong player playing after 9 card did not won trick 
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [9, 'c']]))
        foxintheforest.apply_play(self.game, [0, [9, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertTrue(foxintheforest.valid_step(self.state, [1, [10, 'c']]))
        foxintheforest.apply_play(self.game, [1, [10, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertFalse(foxintheforest.valid_step(self.state, [1, [2, 'c']])) # Wrong player playing after 9 won trick
        self.assertTrue(foxintheforest.valid_step(self.state, [0, [3, 'h']]))

class TestGamePlayed(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.game = foxintheforest.new_game() 
        foxintheforest.play(self.game, [1, [1, 's']])
        foxintheforest.play(self.game, [0, [6, 's']])
        foxintheforest.play(self.game, [1, [8, 'c']])
        foxintheforest.play(self.game, [0, [6, 'c']])
        foxintheforest.play(self.game, [1, [5, 'c']])
        foxintheforest.play(self.game, [1, [10, 'c']])
        foxintheforest.play(self.game, [0, [1, 'c']])
        foxintheforest.play(self.game, [0, [3, 'h']])
        foxintheforest.play(self.game, [0, [11, 'h']])
        foxintheforest.play(self.game, [1, [1, 'h']])

    def test_new_game(self):
        self.assertEqual(len(self.game), 5)
        self.assertDictEqual(self.game, {
            'plays': [[1, [1, 's']], [0, [6, 's']],
                      [1, [8, 'c']], [0, [6, 'c']],
                      [1, [5, 'c']], [1, [10, 'c']], [0, [1, 'c']],
                      [0, [3, 'h']], [0, [11, 'h']], [1, [1, 'h']]],
            'first_player': 1,
            'init_draw_deck': [[3, 'c'], [5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']],
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            })

    def test_copy_game(self):
        game_copy = foxintheforest.copy_game(self.game)
        self.assertDictEqual(game_copy, {
            'plays': [[1, [1, 's']], [0, [6, 's']],
                      [1, [8, 'c']], [0, [6, 'c']],
                      [1, [5, 'c']], [1, [10, 'c']], [0, [1, 'c']],
                      [0, [3, 'h']], [0, [11, 'h']], [1, [1, 'h']]],
            'first_player': 1,
            'init_draw_deck': [[3, 'c'], [5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']],
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            })

    def test_get_state_from_game(self):
        state = foxintheforest.get_state_from_game(self.game)
        self.assertDictEqual(state, {
            'plays': [[1, [1, 's']], [0, [6, 's']],
                      [1, [8, 'c']], [0, [6, 'c']],
                      [1, [5, 'c']], [1, [10, 'c']], [0, [1, 'c']],
                      [0, [3, 'h']], [0, [11, 'h']], [1, [1, 'h']]],
            'private_discards': [[], [[10, 'c']]],
            'trick': [None, None],
            'current_player': 1,
            'leading_player': 1,
            'score': [0, 0],
            'discards': [[[6, 's'], [1, 's'], [3, 'h'], [1, 'h']],
                         [[6, 'c'], [8, 'c'], [1, 'c'], [5, 'c']]],
            'hands': [[[7, 's'], [9, 'c'], [8, 'h'], [6, 'h'], [2, 'h'],
                       [10, 'h'], [11, 's'], [8, 's'], [4, 's']],
                      [[9, 's'], [3, 's'], [2, 'c'], [4, 'c'], [7, 'h'], [2, 's'],
                       [10, 's'], [7, 'c'], [3, 'c']]],
            'init_trump_card': [4, 's'],
            'trump_card': [11, 'h'],
            'draw_deck': [[5, 's'], [4, 'h'], [11, 'c'], [5, 'h'], [9, 'h']]})
    
    def test_get_player_game(self):
        self.assertDictEqual(foxintheforest.get_player_game(self.game, 0), {
            'player': 0,
            'plays': [[1, [1, 's']], [0, [6, 's']],
                      [1, [8, 'c']], [0, [6, 'c']],
                      [1, [5, 'c']], [1, [None, None]], [0, [1, 'c']],
                      [0, [3, 'h']], [0, [11, 'h']], [1, [1, 'h']]],
            'first_player': 1,
            'init_draw_deck': [[None, None]]*6,
            'init_trump_card': [4, 's'],
            'init_hands': [[[3, 'h'], [7, 's'], [11, 'h'], [9, 'c'], [6, 'c'], [1, 'c'],
                            [8, 'h'], [6, 's'], [6, 'h'], [2, 'h'], [10, 'h'], [11, 's'],[8, 's']],
                        [[None, None]]*13]
            }
        )
        self.assertDictEqual(foxintheforest.get_player_game(self.game, 1), {
            'player': 1,
            'plays': [[1, [1, 's']], [0, [6, 's']],
                      [1, [8, 'c']], [0, [6, 'c']],
                      [1, [5, 'c']], [1, [10, 'c']], [0, [1, 'c']],
                      [0, [3, 'h']], [0, [11, 'h']], [1, [1, 'h']]],
            'first_player': 1,
            'init_draw_deck': [[3, 'c'], [None, None], [None, None], [None, None], [None, None], [None, None]],
            'init_trump_card': [4, 's'],
            'init_hands': [[[None, None]]*13,
                           [[1, 's'], [10, 'c'], [5, 'c'], [9, 's'], [3, 's'], [2, 'c'],
                            [1, 'h'], [4, 'c'], [8, 'c'], [7, 'h'], [2, 's'], [10, 's'], [7, 'c']]]
            }
        )

class TestStatePlay(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.game = foxintheforest.new_game()
        self.state = foxintheforest.get_state_from_game(self.game)
        
    def test_list_allowed(self):
        self.assertEqual(foxintheforest.list_allowed(self.state, 0), [])
        self.assertEqual(foxintheforest.list_allowed(self.state, 1), [[1, [1, 's']], [1, [10, 'c']],
            [1, [5, 'c']], [1, [9, 's']], [1, [3, 's']], [1, [2, 'c']], [1, [1, 'h']], [1, [4, 'c']],
            [1, [8, 'c']], [1, [7, 'h']], [1, [2, 's']], [1, [10, 's']], [1, [7, 'c']]])
        self.game = foxintheforest.play(self.game, [1, [2, 'c']])
        self.state = foxintheforest.get_state_from_game(self.game)
        self.assertEqual(foxintheforest.list_allowed(self.state, 1), [])
        self.assertEqual(foxintheforest.list_allowed(self.state, 0), [[0, [9, 'c']], [0, [6, 'c']], [0, [1, 'c']]])

class TestScore(unittest.TestCase):
    def test_score(self):
        random.seed(1)
        self.game = foxintheforest.new_game()
        self.state = foxintheforest.get_state_from_game(self.game)
        while len(self.state["hands"][0]) != 0 or len(self.state["hands"][1]) != 0:
            current_player = self.state["current_player"]
            if current_player == 0:
                selected_play = foxintheforest.list_allowed(self.state, 0)[0]
            else:
                selected_play = foxintheforest.list_allowed(self.state, 1)[0]
            foxintheforest.play(self.game, selected_play)
            self.state = foxintheforest.get_state_from_game(self.game)
        self.assertEqual(foxintheforest.score(self.state), [8, 3])
        
        random.seed(21)
        self.game = foxintheforest.new_game()
        self.state = foxintheforest.get_state_from_game(self.game)
        while len(self.state["hands"][0]) != 0 or len(self.state["hands"][1]) != 0:
            current_player = self.state["current_player"]
            if current_player == 0:
                selected_play = foxintheforest.list_allowed(self.state, 0)[0]
            else:
                selected_play = foxintheforest.list_allowed(self.state, 1)[0]
            foxintheforest.play(self.game, selected_play)
            self.state = foxintheforest.get_state_from_game(self.game)
        self.assertEqual(foxintheforest.score(self.state), [2, 7])
