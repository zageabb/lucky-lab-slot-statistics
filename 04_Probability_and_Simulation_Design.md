# 4. Probability and Simulation Design

## 4.1 Probability model

Prefer explicit reel strips because they make symbol probabilities and stop positions concrete. A model definition contains:

- 5 ordered reel strips, each a list of symbol IDs;
- 3 visible rows per reel;
- payline definitions as row indices across reels;
- a left-to-right paytable for 3, 4, and 5 matching symbols;
- optional wild and scatter rules;
- feature rules and their state transitions;
- allowed stake values;
- metadata and schema version.

For a reel strip of length `L`, each stop has probability `1/L`. Adjacent visible symbols are taken cyclically from the strip. Do not choose every visible cell independently because that destroys reel-strip correlation.

## 4.2 Spin evaluation

For each payline:

1. Read one symbol from each reel at the line’s configured row.
2. Apply documented wild substitution rules.
3. Count consecutive matches from the first reel.
4. Look up the multiplier.
5. Line payout = stake basis × multiplier.

Define clearly whether the displayed stake is total stake or stake per line. Recommended version 1 rule: the selected stake is the total spin stake; paytable multipliers apply to `total_stake / number_of_lines`, represented in integer units so division is exact.

Scatter awards are evaluated independently of paylines and must define whether they add to or replace line wins.

## 4.3 Core statistics

For return random variable `X` measured as payout per one unit wagered:

- Theoretical RTP: `E[X]`.
- House edge: `1 - E[X]`.
- Hit rate: `P(X > 0)`.
- Variance: `E[(X - E[X])²]`.
- Volatility: usually reported here as standard deviation `sqrt(variance)` plus plain-language bands.
- Observed RTP after `n` spins: `sum(payout) / sum(stake)`.

A hit may still pay less than the stake. Therefore separately report:

- any-return rate: `P(payout > 0)`;
- break-even-or-better rate: `P(payout >= stake)`;
- profitable-spin rate: `P(payout > stake)`.

## 4.4 Exact analysis and Monte Carlo

Use exact enumeration when feasible. With reel-strip lengths `L1...L5`, the base-game stop combinations are `L1 × L2 × L3 × L4 × L5`. Evaluate every combination and weight equally when stops are uniform.

Use Monte Carlo when exact enumeration is too large or features introduce extended state. Store:

- seed and generator;
- model definition hash;
- requested and completed spins;
- total wager and payout;
- sample mean, variance, standard error, and confidence interval;
- feature trigger counts;
- elapsed time and software version.

The build must label exact values as **calculated** and Monte Carlo values as **estimated**.

## 4.5 RTP calibration

Do not implement an opaque “target RTP” switch that silently distorts outcomes. Calibration is a design workflow:

1. Start with reel strips and paytable.
2. Calculate or estimate base-game RTP and feature RTP separately.
3. Adjust explicitly identified reel frequencies or payout multipliers.
4. create a new immutable model version;
5. rerun validation and retain the comparison.

If the teacher requests variants such as 80%, 90%, and 96%, Codex must produce three visible model versions whose definitions generate approximately those RTPs, show the measured value and tolerance, and never alter a live model behind the scenes.

Recommended activation tolerance:

- exact enumeration: within ±0.05 percentage points of the labelled value;
- Monte Carlo estimate: target lies within the reported 95% confidence interval and absolute difference is within a configurable tolerance.

## 4.6 Probability sweep experiments

The analysis screen should support controlled comparisons:

- **RTP sweep:** compare several published models.
- **Volatility sweep:** keep RTP approximately constant while redistributing payouts between frequent small wins and rare large wins.
- **Sample-size sweep:** 100, 1,000, 10,000, and 100,000 spins.
- **Stake sweep:** verify that proportional stakes alter credit magnitude but not outcome probability.
- **Bankroll sweep:** estimate risk of ruin for several starting balances.

Each comparison must change one primary factor where practical and document other changed inputs.

## 4.7 Confidence intervals

For independent returns with finite variance, an approximate 95% interval for mean return is:

`sample_mean ± 1.96 × sample_standard_deviation / sqrt(n)`.

The UI must warn that rare jackpots and skewed distributions can make the normal approximation poor at small sample sizes. A bootstrap interval can be added later.

## 4.8 Losing and winning streaks

Define a losing spin as `payout < stake`, not merely `payout == 0`. Record both zero-return streaks and net-losing streaks.

The next independent spin retains the same probability after a streak. The application should demonstrate this by comparing conditional empirical rates after streaks with the overall rate, alongside uncertainty and sample size.

## 4.9 Forbidden adaptive behaviour

Participant outcomes must not use player name, balance, lifetime spend, recent losses, recent wins, session length, or classroom identity as RNG inputs or probability modifiers.

If adaptive odds are ever studied academically, they must be implemented only in a separate simulation namespace, visibly labelled as a hypothetical non-standard experiment, and must never be selectable for participant play.

## 4.10 Reference pseudocode

```python
def spin(model, stake_units, rng):
    stops = [rng.randrange(len(strip)) for strip in model.reel_strips]
    board = visible_board(model.reel_strips, stops, model.rows)
    line_awards = evaluate_paylines(board, model.paylines, model.paytable, stake_units)
    feature_awards, feature_state = evaluate_features(board, model, stake_units, rng)
    payout_units = sum(line_awards) + sum(feature_awards)
    return SpinOutcome(
        stops=stops,
        board=board,
        line_awards=line_awards,
        feature_awards=feature_awards,
        payout_units=payout_units,
        feature_state=feature_state,
    )
```

