from .game_engine import ModelDefinition

SYMBOLS = {
    "clover": "Four-leaf clover", "harp": "Celtic-inspired harp", "horseshoe": "Upright horseshoe",
    "rainbow": "Rainbow", "emerald": "Emerald gemstone", "crown": "Gold crown", "gold_pot": "Pot of virtual gold",
}

BASELINE = ModelDefinition(
    name="Meadow Baseline",
    symbols=SYMBOLS,
    reels=[
        ["clover", "harp", "horseshoe", "clover", "emerald", "rainbow", "crown", "gold_pot"],
        ["clover", "horseshoe", "harp", "emerald", "clover", "crown", "rainbow", "gold_pot"],
        ["harp", "clover", "horseshoe", "rainbow", "emerald", "clover", "crown", "gold_pot"],
        ["clover", "harp", "emerald", "horseshoe", "rainbow", "clover", "gold_pot", "crown"],
        ["horseshoe", "clover", "harp", "emerald", "clover", "rainbow", "crown", "gold_pot"],
    ],
    paylines=[[0,0,0,0,0],[1,1,1,1,1],[2,2,2,2,2],[0,1,2,1,0],[2,1,0,1,2]],
    paytable={
        "clover": {3: 15, 4: 38, 5: 112}, "harp": {3: 19, 4: 45, 5: 150},
        "horseshoe": {3: 19, 4: 52, 5: 169}, "rainbow": {3: 30, 4: 75, 5: 262},
        "emerald": {3: 38, 4: 112, 5: 375}, "crown": {3: 45, 4: 150, 5: 525},
        "gold_pot": {3: 56, 4: 225, 5: 825},
    },
    allowed_stakes=[100, 200, 500],
)
