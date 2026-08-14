# 7. Desktop Codex Master Build Brief

Copy this whole file into Desktop Codex with the other design documents available in the repository.

---

## Instructions to Codex

Build the complete **Lucky Lab: Slot Statistics Simulator** described by the accompanying documents. It is a local, browser-based classroom study of slot-game probability and virtual-credit accounting.

Do not stop after producing another plan. Inspect the full repository first, report a concise audit, then implement the application phase by phase unless a genuine blocker requires a user decision.

### Authoritative documents

Read these completely before changing code:

1. `README.md`
2. `01_Product_Vision_and_Scope.md`
3. `02_Functional_and_Nonfunctional_Requirements.md`
4. `03_Architecture_and_Data_Design.md`
5. `04_Probability_and_Simulation_Design.md`
6. `05_UX_and_Classroom_Workflows.md`
7. `06_Test_and_Acceptance_Plan.md`
8. `08_Visual_Design_and_Asset_Brief.md`

If a requirement conflicts with an implementation shortcut, the documents win. Ask only where two requirements materially conflict or a choice would irreversibly change the product.

## Non-negotiable boundaries

- No real money, payments, prizes, withdrawals, deposits, gambling accounts, or public hosting.
- Call values **virtual credits** in the interface.
- Bind to `127.0.0.1` by default.
- Do not reproduce Rainbow Riches branding, assets, sounds, exact UI, paytable, reel strips, bonus names, or proprietary maths.
- Create original generic symbols and styling.
- Use the supplied original concept graphics as the visual reference. Do not use them as justification to copy any commercial game.
- Never alter participant odds based on name, balance, cumulative spend, wins, losses, streaks, session duration, or previous outcomes.
- Never claim a player is due a win.
- Participant outcomes are calculated on the server.
- The append-only ledger is authoritative for every balance and spend total.
- Simulation records are separate from participant records.
- Published probability models are immutable and versioned.
- Use integer minor units for all credit values; do not use float for accounting.
- Do not add an LLM, external service, telemetry, CDN, or API dependency.

## Required stack

- Python 3.12 or later.
- Flask application factory with blueprints.
- SQLAlchemy 2.x.
- Alembic via Flask-Migrate.
- SQLite with foreign keys and WAL enabled.
- Pydantic for validated game-model definitions and service DTOs.
- Bootstrap 5, stored locally, plus minimal local JavaScript/CSS.
- Chart.js or Plotly.js stored locally.
- Pytest; use Hypothesis for valuable property tests.
- Ruff and a type checker such as mypy or pyright.

Prefer a simple server-rendered Flask application. Do not introduce React, Docker, Celery, Redis, or a separate API service unless the existing repository already depends on them and retaining them is demonstrably simpler.

## Phase 0 — Repository audit and implementation map

Before editing:

1. Read the complete repository and all design documents.
2. Identify existing patterns, dependencies, migrations, tests, and reusable components.
3. Provide a compact table: **reuse / refactor / replace / create**.
4. Show the intended directory structure, database migration plan, and implementation sequence.
5. Identify assumptions and blockers.
6. Continue directly to Phase 1 if there is no genuine blocker.

Do not delete or overwrite unrelated user work. Preserve existing behaviour unless the brief explicitly changes it.

## Phase 1 — Executable skeleton and persistence

Deliver:

- application factory, configuration, extensions, blueprints, templates, and local static assets;
- SQLAlchemy entities and first migration for players, sessions, game models/versions, spins, ledger entries, simulation runs, and trials;
- SQLite constraints, foreign keys, useful indexes, and WAL configuration;
- service boundaries and Pydantic schemas;
- health/home page and navigation;
- setup, migrate, run, and test commands;
- tests that create the database solely through migrations.

Exit criterion: a clean checkout installs, migrates, starts locally, and passes foundational tests.

## Phase 2 — Deterministic game engine

Implement the engine as a framework-independent Python package:

- explicit cyclic reel strips;
- server-selected reel stops;
- visible 5 × 3 board;
- configurable paylines and paytable;
- wild/scatter extension points;
- complete evaluation DTO;
- exact enumeration for feasible base models;
- seeded Monte Carlo analysis;
- original baseline model with a clearly documented definition;
- original production-ready reel-symbol assets derived from the supplied style board, saved as individual assets with accessible text equivalents;
- unit, property, and statistical tests.

Keep RNG selection behind an adapter. Participant play and simulation use different configured RNG providers.

Exit criterion: a tiny hand-verifiable model passes exact probability tests, and the baseline model reports documented RTP, hit rate, and variance calculation method.

## Phase 3 — Player play and authoritative ledger

Implement:

- player name entry/selection;
- virtual-credit allocation;
- play sessions;
- stake validation;
- atomic spin, wager, and payout posting;
- idempotency token protection;
- balance and spend derived through ledger service;
- spin audit view;
- original responsive play interface;
- visual consistency with the supplied play-screen concept while keeping all statistics and educational notices legible;
- classroom-only labelling and neutral outcome language.

Do not allow routes or UI code to write balances directly.

Exit criterion: the individual accounting acceptance scenario passes and database rollback/idempotency are proven by tests.

## Phase 4 — Model laboratory

Implement:

- list and inspect models;
- clone a published version to draft;
- structured editor for primary inputs with an advanced JSON view;
- schema and domain validation;
- exact or estimated theoretical statistics;
- immutable publish and explicit activate actions;
- archive without deleting history;
- comparison of model versions;
- supplied teaching variants, including examples with different RTP and examples with similar RTP but different volatility.

Clearly show which values are exact and which are estimates. Store model definition hashes.

Exit criterion: a teacher can change one input, validate it, publish a new version, compare it, and activate it without changing historical results.

## Phase 5 — Simulations and statistics

Implement:

- batch configuration for model, seed, trials, spins, starting bankroll, stake, and stop-at-zero;
- efficient chunked execution with progress reporting that does not hold one long transaction;
- summary metrics listed in the requirements;
- RTP convergence, bankroll path, ending-balance distribution, payout distribution, and streak views;
- visual consistency with the supplied analysis-dashboard concept;
- RTP, volatility, sample-size, stake, and bankroll comparisons;
- CSV exports that include configuration and model hash;
- optional background job implemented with an in-process worker and persistent job state, recoverable after an interrupted run. Do not add Redis/Celery.

Exit criterion: seeded runs reproduce, do not mutate player data, and complete the performance target.

## Phase 6 — Classroom reporting and learning content

Implement:

- individual player statistics and full ledger;
- class/cohort analysis;
- session and spin drill-down;
- printable/exportable experiment summary;
- embedded explanations of RTP, hit rate, volatility, house edge, variance, sample size, confidence intervals, re-wagered credits, and the gambler’s fallacy;
- reset-demo-data flow with confirmation and export-first suggestion.

Avoid competitive rankings that encourage larger wagers or losses.

## Phase 7 — Hardening and handover

Complete:

- accessibility review;
- input validation and error states;
- transaction/concurrency review;
- performance profiling for simulation;
- migration-from-empty and upgrade tests;
- deterministic tests with fixed seeds;
- backup/restore and reset scripts;
- complete README and teacher quick-start;
- full test, lint, type-check, and launch verification.

Do not add authentication; document that there is no secure teacher boundary and that LAN exposure is not the default.

## Required reporting after every phase

After each phase, report:

1. files created or changed;
2. migrations added and how to apply them;
3. exact commands run;
4. test/lint/type-check results;
5. local launch command and URL;
6. a short manual demo workflow;
7. known limitations or risks;
8. the next phase;
9. a concise suggested commit message.

Continue to the next phase unless blocked or explicitly asked to pause.

## Final acceptance demonstration

At handover, demonstrate:

1. create `Student A` and allocate 100 virtual credits;
2. complete spins at two stakes;
3. prove balance from ledger entries;
4. show cumulative wagered can exceed the original allocation through re-wagering;
5. inspect one spin’s paylines and payout calculation;
6. clone and publish a probability-model version;
7. compare at least two model simulations using recorded seeds;
8. show short-run observed RTP differing from theoretical RTP;
9. export a player ledger and an experiment result;
10. restart the app and confirm persistence.

The final response must give the exact installation, migration, launch, test, backup, restore, and reset commands, together with the local URL and any remaining limitations.

---

End of Desktop Codex brief.
