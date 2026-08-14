import random

import pytest

from app.baseline import BASELINE
from app.game_engine import ModelDefinition, exact_statistics, spin, visible_board


def test_visible_board_wraps_reel_strips():
    board = visible_board(BASELINE, [7, 7, 7, 7, 7])
    assert board[1][0] == BASELINE.reels[0][0]
    assert len(board) == 3 and all(len(row) == 5 for row in board)


def test_seeded_spin_is_reproducible_and_stake_does_not_change_stops():
    one = spin(BASELINE, 100, random.Random(42))
    two = spin(BASELINE, 500, random.Random(42))
    assert one.stops == two.stops
    assert two.payout_units == one.payout_units * 5


def test_tiny_model_exact_result_is_hand_verifiable():
    tiny = ModelDefinition(name="tiny", symbols={"a":"A","b":"B"},
        reels=[["a","b"] for _ in range(5)], paylines=[[1,1,1,1,1]],
        paytable={"a":{5:2},"b":{5:2}}, allowed_stakes=[100])
    stats = exact_statistics(tiny)
    assert stats["combinations"] == 32
    assert stats["hit_rate"] == pytest.approx(2/32)
    assert stats["rtp"] == pytest.approx(4/32)


def test_definition_hash_is_canonical():
    assert BASELINE.canonical_hash() == ModelDefinition.model_validate_json(BASELINE.model_dump_json()).canonical_hash()
