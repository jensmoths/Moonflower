"""Regression tests for the offline game engine and CLI."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import moonflower as game


class EngineTests(unittest.TestCase):
    def test_growth_is_cyclic_and_moonflower_reacts_differently(self):
        species = ["G", "M", "G", "G", "G", "G", "G", "G", "G"]
        board = [0] * 9
        self.assertEqual(game.apply_action(board, species, 3, "sun", 1)[1], 2)
        self.assertEqual(game.apply_action(board, species, 3, "rain", 1)[1], 1)
        self.assertEqual(board, [0] * 9)  # pure function

    def test_sun_influences_north_and_rain_horizontal(self):
        board = [0] * 9
        species = ["G"] * 9
        self.assertEqual(game.apply_action(board, species, 3, "sun", 4), [0, 1, 0, 0, 1, 0, 0, 0, 0])
        self.assertEqual(game.apply_action(board, species, 3, "rain", 3), [0, 0, 0, 1, 1, 0, 0, 0, 0])

    def test_wind_rotates_stages_not_species(self):
        board = [0, 1, 2, 0, 1, 2, 0, 1, 2]
        self.assertEqual(game.apply_action(board, ["G"] * 9, 3, "wind", 1),
                         [0, 1, 2, 2, 0, 1, 0, 1, 2])

    def test_all_levels_reproducible_and_solvable(self):
        for level in game.LEVELS:
            for seed in range(50):
                with self.subTest(level=level, seed=seed):
                    first = game.generate_game(level, seed)
                    second = game.generate_game(level, seed)
                    for key in ("cells", "species", "targets", "size", "budget"):
                        self.assertEqual(first[key], second[key])
                    self.assertLess(game.progress(first["cells"], first["targets"]), len(first["targets"]))
                    if level >= 4:
                        self.assertTrue(any(first["species"][i] == "M" for i in first["targets"]))

    def test_cell_validation(self):
        self.assertEqual(game.cell_index("b2", 3), 4)
        for cell in ("D1", "B0", "X9", "33", "A", "A-2"):
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                game.cell_index(cell, 3)


class TerminalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = game.main(["--home", str(self.home), *args])
        return code, out.getvalue(), err.getvalue()

    def test_play_save_replay_and_json(self):
        code, text, _ = self.run_cli("start", "--seed", "101", "--level", "4")
        self.assertEqual(code, 0)
        self.assertIn("M=unfamiliar", text)
        code, text, _ = self.run_cli("look", "--json")
        self.assertEqual(code, 0)
        initial = json.loads(text)
        self.assertEqual(len(initial["board"]), 9)
        code, _, _ = self.run_cli("rain", "A1")
        self.assertEqual(code, 0)
        code, text, _ = self.run_cli("replay", "--last", "1")
        self.assertEqual(code, 0)
        self.assertIn("TURN 1", text)
        self.assertIn("Moves: 1/14", text)
        self.assertEqual(game.load_session(self.home)["moves"][0]["turn"], 1)

    def test_guard_active_session_and_force_abandon(self):
        self.run_cli("start")
        code, _, err = self.run_cli("start", "--seed", "22")
        self.assertEqual(code, 2)
        self.assertIn("in progress", err)
        code, _, _ = self.run_cli("start", "--seed", "22", "--force")
        self.assertEqual(code, 0)
        items = json.loads((self.home / "results.jsonl").read_text().splitlines()[0])
        self.assertEqual(items["outcome"], "abandoned")

    def test_invalid_move_does_not_mutate_state(self):
        self.run_cli("start")
        before = (self.home / "session.json").read_text()
        code, _, err = self.run_cli("sun", "Z99")
        self.assertEqual(code, 2)
        self.assertIn("outside", err)
        self.assertEqual((self.home / "session.json").read_text(), before)

    def test_scoreboard_and_guide(self):
        self.assertEqual(self.run_cli("results")[1].strip(), "No completed games yet.")
        self.assertIn("intentionally undocumented", self.run_cli("guide")[1])


if __name__ == "__main__":
    unittest.main()
