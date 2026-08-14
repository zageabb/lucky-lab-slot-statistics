from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from itertools import product
from statistics import fmean, pvariance

from pydantic import BaseModel, Field, model_validator


class ModelDefinition(BaseModel):
    schema_version: int = 1
    name: str
    rows: int = 3
    reels: list[list[str]]
    paylines: list[list[int]]
    paytable: dict[str, dict[int, int]]
    allowed_stakes: list[int] = Field(min_length=1)
    symbols: dict[str, str]

    @model_validator(mode="after")
    def validate_domain(self):
        if len(self.reels) != 5 or self.rows != 3:
            raise ValueError("version 1 requires five reels and three rows")
        if any(len(line) != 5 or any(r < 0 or r >= self.rows for r in line) for line in self.paylines):
            raise ValueError("each payline needs five valid row indexes")
        known = set(self.symbols)
        if any(symbol not in known for reel in self.reels for symbol in reel):
            raise ValueError("reel contains an unknown symbol")
        if any(s <= 0 or s % len(self.paylines) for s in self.allowed_stakes):
            raise ValueError("stakes must divide exactly across paylines")
        return self

    def canonical_hash(self) -> str:
        raw = json.dumps(self.model_dump(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass(frozen=True)
class Outcome:
    stops: list[int]
    board: list[list[str]]
    line_awards: list[dict]
    payout_units: int

    def json(self) -> dict:
        return asdict(self)


def visible_board(model: ModelDefinition, stops: list[int]) -> list[list[str]]:
    return [[model.reels[col][(stops[col] + row) % len(model.reels[col])] for col in range(5)] for row in range(model.rows)]


def evaluate_board(model: ModelDefinition, board: list[list[str]], stake_units: int) -> tuple[list[dict], int]:
    line_stake = stake_units // len(model.paylines)
    awards: list[dict] = []
    total = 0
    for number, rows in enumerate(model.paylines, 1):
        symbols = [board[rows[col]][col] for col in range(5)]
        first = symbols[0]
        matches = 1
        for symbol in symbols[1:]:
            if symbol != first:
                break
            matches += 1
        multiplier = model.paytable.get(first, {}).get(matches, 0)
        payout = line_stake * multiplier
        total += payout
        awards.append({"line": number, "rows": rows, "symbols": symbols, "matches": matches, "multiplier": multiplier, "payout_units": payout})
    return awards, total


def spin(model: ModelDefinition, stake_units: int, rng: random.Random) -> Outcome:
    stops = [rng.randrange(len(strip)) for strip in model.reels]
    board = visible_board(model, stops)
    awards, payout = evaluate_board(model, board, stake_units)
    return Outcome(stops, board, awards, payout)


def exact_statistics(model: ModelDefinition, stake_units: int | None = None) -> dict:
    stake = stake_units or model.allowed_stakes[0]
    returns = []
    hits = 0
    for stops in product(*(range(len(reel)) for reel in model.reels)):
        board = visible_board(model, list(stops))
        _, payout = evaluate_board(model, board, stake)
        value = payout / stake
        returns.append(value)
        hits += payout > 0
    mean = fmean(returns)
    return {"rtp": mean, "hit_rate": hits / len(returns), "variance": pvariance(returns), "combinations": len(returns), "method": "exact"}


def confidence_interval(returns: list[float]) -> tuple[float, float]:
    if len(returns) < 2:
        return (returns[0] if returns else 0.0,) * 2
    mean = fmean(returns)
    margin = 1.96 * math.sqrt(pvariance(returns)) / math.sqrt(len(returns))
    return mean - margin, mean + margin
