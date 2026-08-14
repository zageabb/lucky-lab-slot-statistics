# 1. Product Vision and Scope

## 1.1 Vision

Build a transparent classroom laboratory that lets students play and simulate a virtual slot game, alter its probability model, and see how return to player (RTP), hit rate, volatility, stake size, sample size, and chance affect results.

No real money, prizes, deposits, withdrawals, payment processing, advertising, or monetisation are permitted. All values are labelled **virtual credits**. The application is an educational statistics tool, not a gambling product.

## 1.2 Educational questions

The application should help answer:

- Why can an individual lose even when the theoretical RTP is high?
- Why does a game with 96% RTP not return exactly 96 credits from every 100 credits wagered?
- How do results converge as the number of spins increases?
- How do hit rate and volatility differ from RTP?
- What is the difference between credits added, credits wagered, payouts, net result, and current balance?
- How does re-wagering the same credits make cumulative spend exceed the initial allocation?
- How does a confidence interval help interpret an observed RTP?
- Why does a run of losses not make a win “due” on an independent next spin?

## 1.3 Product identity

Working title: **Lucky Lab: Slot Statistics Simulator**.

Use original symbols and styling, for example clover, harp, horseshoe, rainbow, gem, crown, and pot. Do not use the Rainbow Riches product name in the interface or repository name. Do not reproduce its assets, exact layout, animations, sounds, paytable, bonus presentation, or claimed probability model.

## 1.4 Users

- **Participant:** enters a display name, receives virtual credits, plays spins, and reviews personal results.
- **Teacher/analyst:** creates or selects a probability model, runs batch simulations, compares players and cohorts, exports data, and resets classroom data.

There is no authentication or authorisation in version 1. The teacher screen is therefore a convenience view, not a secure administrative boundary.

## 1.5 In scope for version 1

- Enter or select a display name.
- Add an explicitly labelled allocation of virtual credits.
- Choose stake per spin within configured limits.
- Play a visually represented 5-reel, 3-row game.
- Resolve wins using documented paylines and a configurable paytable.
- Maintain an immutable transaction ledger for allocations, wagers, payouts, adjustments, and resets.
- Show player balance, total allocated, cumulative wagered, total payout, net result, observed RTP, hit rate, and spins.
- Store every spin with the game-model version used.
- Create, clone, edit, validate, activate, and archive game-model versions.
- Run seeded Monte Carlo simulations without affecting player balances.
- Sweep a parameter or compare several models.
- Display bankroll path, return distribution, observed RTP convergence, win-size distribution, and losing-streak statistics.
- Export players, sessions, spins, ledger entries, and simulation results to CSV.
- Include classroom explanations and warnings about variance and the gambler’s fallacy.

## 1.6 Explicitly out of scope

- Real money or items of value.
- Payments, cash-out, prizes, wagering against other people, leaderboards that reward gambling, or social pressure features.
- Accounts, passwords, permissions, remote access, public hosting, or cloud synchronisation.
- Reproducing a commercial game’s proprietary mathematics.
- Per-player or loss-triggered manipulation of odds.
- “Near miss” manipulation, forced wins, retention targeting, dark patterns, autoplay for participants, or celebratory treatment of losses.
- AI/LLM dependency in version 1.

## 1.7 Core principles

1. **Transparent maths:** every probability and payout setting is inspectable and versioned.
2. **Independent outcomes:** participant spins use the active model and do not depend on personal win/loss history.
3. **Ledger authority:** financial-style totals are derived from transactions.
4. **Reproducibility:** simulation runs accept and store a random seed.
5. **Separation:** participant play and analytical simulations are stored separately.
6. **Local first:** bind to loopback and use SQLite.
7. **Original design:** use generic, newly created visual treatment and assets.

