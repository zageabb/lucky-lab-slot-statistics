# 6. Test and Acceptance Plan

## 6.1 Unit tests

- Reel wrapping and visible-board construction.
- Payline evaluation for 0, 2, 3, 4, and 5 matches.
- Wild and scatter edge cases.
- Total-stake allocation across paylines without rounding loss.
- Feature state transitions.
- Model JSON validation and canonical hashing.
- Ledger balance calculation.
- Player metric calculations with no spins and with mixed results.
- Streak and maximum-drawdown algorithms.
- Confidence interval and percentile calculations.
- Seeded simulation reproducibility.

## 6.2 Invariant/property tests

- Payouts and stakes never become negative.
- Board symbols always exist in the referenced model.
- Exactly one stop is selected per reel.
- Every completed spin’s ledger delta equals `payout - stake`.
- Replaying an idempotency token never creates a second debit.
- Published model versions never change.
- Participant spin probabilities do not read player or ledger data.
- Simulation services never write participant ledger rows.

Use Hypothesis where it adds value.

## 6.3 Statistical tests

Statistical tests must use fixed seeds, large enough samples, and tolerance based on expected sampling error. They must not assert that a random sample equals the theoretical RTP exactly.

- For a tiny model, compare exact enumeration against hand-calculated probabilities.
- Compare Monte Carlo estimates with exact values using a tolerance derived from standard error.
- Confirm symbol stop frequencies are approximately uniform over reel positions.
- Confirm that changing a player name or balance does not change a seeded engine outcome when all engine inputs are otherwise equal.
- Confirm stake scaling changes payouts proportionally but not selected stops.
- Confirm supplied example RTP variants meet their documented validation tolerance.

## 6.4 Integration tests

- Create player and reject case-insensitive duplicate.
- Allocate credits and verify ledger/balance.
- Start session, spin, and verify atomic records.
- Reject invalid stake and insufficient balance.
- Retry a spin request and verify idempotency.
- End session and prevent subsequent spins.
- Clone, validate, publish, and activate a model version.
- Prevent direct edit of a published version.
- Run and export a simulation.
- Export player ledger with correct totals.
- Reset demo data with confirmation while retaining schema and supplied baseline models.

## 6.5 Migration and persistence tests

- Create a database from empty using migrations only.
- Upgrade from each committed migration checkpoint.
- Verify foreign keys, unique constraints, and indexes.
- Restart the server and confirm players, models, sessions, and ledgers persist.
- Back up the SQLite file and restore it into a clean instance.

## 6.6 Manual acceptance scenarios

### Scenario 1 — Individual accounting

1. Create `Student A` with 100.00 virtual credits.
2. Play at least ten spins at two stake values.
3. Verify every change appears in the ledger.
4. Confirm balance equals allocations minus wagers plus payouts.
5. Confirm cumulative wagered counts re-wagered credits.

### Scenario 2 — Model comparison

1. Publish two models with different RTP or volatility.
2. Run at least 100 trials of 10,000 spins for each with documented seeds.
3. Compare distribution, not only average return.
4. Export both configurations and results.

### Scenario 3 — Independence

1. Identify a long losing streak in a large simulation.
2. Compare next-spin results after streaks with the overall next-spin rate.
3. Verify the application does not claim the next spin is due to win.

## 6.7 Definition of done

- All Must requirements are implemented.
- Production and test dependencies install from documented commands.
- Migrations create a working database.
- Automated tests pass.
- A baseline model has validated published maths and original assets.
- Participant and simulation workflows work without internet access.
- Ledger invariants have tests and database constraints where practical.
- The README includes setup, launch, test, backup, restore, reset, and export instructions.
- No commercial brand name or copied asset appears in the delivered application.
- No real-money or payment capability exists.

