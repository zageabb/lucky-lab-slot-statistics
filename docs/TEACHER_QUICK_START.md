# Teacher quick start

Lucky Lab is an educational probability simulator. Every value is a virtual credit with no monetary value.

Start with 100 spins at a fixed 1.00 stake. Ask learners to predict whether everyone will observe the exact model RTP, then compare observed RTP, ending balance, hit rate, and losing streaks. Repeat with 1,000 and 10,000 seeded spins. Emphasise that wider samples generally converge but do not move smoothly.

For a controlled model comparison, clone the published baseline, alter one explicit paytable multiplier, validate and publish the draft, then run both versions using the same seed, spin count, trial count, stake, and bankroll. Record the immutable model hashes in exported CSV files.

The cumulative-wager figure counts re-wagered returns, so it can exceed the initial allocation. A losing streak does not make the next result due. Stake scales credit amounts but does not change stop selection probabilities.
