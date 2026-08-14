# 5. UX and Classroom Workflows

## 5.1 Visual direction

Create an original, bright laboratory-meets-folklore design. Use dark navy or deep green backgrounds, high-contrast cream panels, restrained gold accents, and original flat symbols. The analytical screens should feel like a statistics lab rather than a commercial casino.

Avoid copying any commercial game cabinet, logo, typography, reel frame, feature name, mascot, audio cue, or animation. Do not use flashing loss-chasing prompts or misleading near-win emphasis.

## 5.2 Navigation

- **Play** — select player, allocate virtual credits, start session, choose stake, spin, and inspect result.
- **My statistics** — individual totals, bankroll chart, session table, streaks, and ledger.
- **Class analysis** — anonymised or named cohort summaries and distributions.
- **Simulations** — configure, run, compare, and export experiments.
- **Game models** — view definitions, clone draft, edit, validate, publish, activate, archive.
- **Learn** — RTP, hit rate, volatility, independence, variance, confidence intervals, and gambler’s fallacy.

## 5.3 Play screen

First viewport:

- educational-only banner;
- player name/selector;
- virtual-credit balance;
- cumulative wagered and total payout;
- 5 × 3 reel grid;
- stake selector;
- one clear Spin button;
- result summary in neutral language;
- expandable “How this result was calculated” panel.

After a spin, show stake deducted, payout added, net change, paylines/features evaluated, and updated balance. A zero or net-loss result should not be celebrated or disguised.

## 5.4 Player statistics

Display:

- allocated credits;
- current balance;
- cumulative wagered;
- total payout;
- net play result;
- spins;
- observed RTP versus model RTP;
- any-return, break-even-or-better, and profitable-spin rates;
- longest zero-return and net-losing streaks;
- bankroll-over-spin chart;
- session history and downloadable ledger.

Include the note: “Cumulative wagered can be greater than allocated credits because the same credits and any winnings may be wagered more than once.”

## 5.5 Teacher workflow

1. Open Game models and clone the supplied baseline.
2. Change one clearly identified probability or payout input.
3. Validate and calculate/estimate model statistics.
4. Publish the version.
5. Run matched simulations using the same seed plan and trial counts.
6. Compare RTP, spread, risk of ruin, and streaks.
7. Activate a model for participant play if required.
8. Export the experiment configuration and results.

## 5.6 Suggested classroom exercises

### Exercise A — Short-run variance

Give each student 100 virtual credits and 100 spins at a fixed stake. Compare the range of observed RTP and ending balances.

### Exercise B — Convergence

Run 100, 1,000, 10,000, and 100,000 spins using the same model. Plot observed RTP and its distance from theoretical RTP.

### Exercise C — Same RTP, different volatility

Compare two models with approximately equal RTP: one with frequent small returns and one with rarer large returns.

### Exercise D — Re-wagered credits

Compare allocated credits with cumulative wagered and explain why the latter can be much larger.

### Exercise E — Streak fallacy

Measure the next-spin win rate after zero, three, five, and ten consecutive net-losing spins. Discuss sampling error and independence.

## 5.7 Accessibility and interaction

- All controls have visible labels and keyboard focus.
- Reel symbols include text or accessible names.
- Charts have table alternatives and downloadable CSV.
- Animation respects `prefers-reduced-motion`.
- Spin can be triggered by button or keyboard, but rapid repeated input is locked until the request completes.
- Status changes are announced through an ARIA live region.
- Use both icons/text and colour for win/loss states.

