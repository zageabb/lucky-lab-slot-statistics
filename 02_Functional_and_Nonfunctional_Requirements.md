# 2. Functional and Non-functional Requirements

## 2.1 Player and session requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | A user can create or select a player using a display name. | Must |
| FR-002 | Names are trimmed; blank names are rejected; duplicate matching is case-insensitive. | Must |
| FR-003 | Starting credits are added as a ledger allocation, not written directly to balance. | Must |
| FR-004 | A player can start and end a play session. | Must |
| FR-005 | The interface displays that all values are virtual and have no monetary value. | Must |
| FR-006 | A teacher can deactivate a player while retaining history. | Should |

## 2.2 Spin requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-010 | A player selects a permitted stake and requests one spin. | Must |
| FR-011 | The server validates the stake and available balance. | Must |
| FR-012 | The wager debit and payout credit are committed atomically with the spin result. | Must |
| FR-013 | The spin stores its model version, stake, board, evaluated paylines, payout, timestamps, and random audit data. | Must |
| FR-014 | The next spin is statistically independent of the player’s previous result, except where an explicitly documented feature state is part of the model. | Must |
| FR-015 | Client-side code cannot decide or alter the result. | Must |
| FR-016 | Double-clicks and repeated requests cannot charge twice; use a unique request/idempotency token. | Must |
| FR-017 | Insufficient balance prevents the spin without creating ledger entries. | Must |

## 2.3 Virtual-credit accounting

| Metric | Definition |
|---|---|
| Allocated credits | Sum of positive `ALLOCATION` ledger entries. |
| Cumulative wagered (“spend”) | Absolute sum of `WAGER` debits. This includes re-wagered winnings. |
| Total payout | Sum of `PAYOUT` credits. |
| Net play result | `total_payout - cumulative_wagered`. |
| Current balance | Sum of all ledger amounts for the player. |
| Observed RTP | `total_payout / cumulative_wagered`, when wagered is non-zero. |
| Hit rate | Spins with payout greater than zero divided by completed spins. |
| Profit/loss from allocation | `current_balance - allocated_credits - net_adjustments`. |

All stored credit amounts use integer minor credit units. For example, one display credit may equal 100 units. Never use binary floating-point for balances, stakes, or payouts.

## 2.4 Game-model management

- A model has a stable ID and immutable numbered versions.
- Editing a published model creates a draft version.
- A draft cannot become active until validation passes.
- Only one model version is active for participant play at a time.
- Old versions remain readable so historical spins are reproducible.
- Configurable fields include reel strips or symbol weights, rows, reels, paylines, paytable, stake options, feature rules, and display metadata.
- The system calculates or estimates theoretical RTP, hit rate, and volatility for the model and records the calculation method, sample size, seed, and uncertainty.
- A model with invalid symbols, impossible paylines, negative payouts, or inconsistent feature definitions cannot be activated.
- Model activation does not change earlier player or simulation records.

## 2.5 Analysis and simulation

- Run batches of 1,000; 10,000; 100,000; or a custom bounded number of spins.
- Configure starting bankroll, fixed stake, number of virtual players, model version, and seed.
- Stop a simulated player at zero balance when overdraft is disabled.
- Do not post simulation wagers or payouts to the participant ledger.
- Calculate mean, median, standard deviation, observed RTP, hit rate, maximum drawdown, longest losing streak, risk of ruin, ending-bankroll distribution, and selected percentiles.
- Support repeated experiments across target RTP/model variants.
- Show expected house edge as `1 - theoretical RTP`.
- Where valid, show a 95% confidence interval for the sample mean return and explain its assumptions.
- Export input configuration and results together so the experiment is reproducible.

## 2.6 Reports

- Player summary and transaction ledger.
- Individual session detail.
- Spin audit view showing how a payout was evaluated.
- Cohort comparison, with a warning that names are identifiers and results are random.
- Model comparison.
- Simulation run detail.
- CSV export. JSON export is optional.

## 2.7 Classroom safeguards

- Persistent banner: “Educational simulation — virtual credits only — no monetary value.”
- Explain that RTP is a long-run expectation, not a promise for a session.
- Do not say a win is “due,” that odds improve after losses, or that a player can recover by increasing stakes.
- No real currency symbol in the participant UI.
- No deposit, withdraw, cash-out, or payment terminology.
- Provide `Reset demo data` with a clear confirmation and optional CSV export first.
- Include an optional neutral session timer and total-spend reminder.
- Avoid rankings by largest wager or biggest loss.

## 2.8 Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-001 | Runs on Windows, macOS, and Linux with documented setup. |
| NFR-002 | Binds to `127.0.0.1` by default; LAN binding requires an explicit command-line/config change. |
| NFR-003 | Standard spin response target is below 300 ms on an ordinary desktop, excluding intentional animation. |
| NFR-004 | A 100,000-spin simulation completes without holding a database transaction for the whole run. |
| NFR-005 | Database writes are transactional; SQLite foreign keys and WAL mode are enabled. |
| NFR-006 | Model JSON is schema-validated and canonicalised before hashing/versioning. |
| NFR-007 | Pages are usable with keyboard controls and screen readers; colour is not the only state cue. |
| NFR-008 | Automated tests cover maths, ledger invariants, routes, migrations, exports, and seeded reproducibility. |
| NFR-009 | No external network, API key, telemetry, advertising, or CDN is required after installation. |
| NFR-010 | Application logs must not contain full exported datasets or unnecessary player data. |

