# Lucky Lab: Slot Statistics Simulator

A local, server-rendered classroom laboratory for studying RTP, hit rate, volatility, bankroll paths, streaks, sample size, and virtual-credit accounting. It has no real money, prizes, payments, telemetry, CDN, accounts, or public hosting.

## Quick start

Python 3.12 or later is required.

```bash
cd classroom-slot-statistics-lab
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/flask --app app:create_app db upgrade
.venv/bin/flask --app app:create_app main seed
.venv/bin/python -m app
```

Open <http://127.0.0.1:5020> on the host computer, or `http://HOST-LAN-IP:5020` from another device on the same network. The project launcher binds to `0.0.0.0:5020`. There is deliberately no secure teacher boundary, so use it only on a trusted classroom LAN and never expose the port to the public internet.

## Verify

```bash
.venv/bin/pytest -q
.venv/bin/ruff check app tests
.venv/bin/mypy app
```

## Classroom workflow

1. Create `Student A` with 100.00 virtual credits.
2. Start a session and spin at 1.00 and 2.00 stakes.
3. Open a result’s calculation audit and export the ledger.
4. Clone the baseline model, change a visible reel or paytable input, validate, publish, and activate it.
5. Run matched seeded experiments and compare distributions, not only average return.
6. Use the Learn page to discuss convergence, re-wagering, confidence intervals, and the gambler’s fallacy.

The ledger is append-only during normal operation. Balance is always its sum. A completed spin atomically creates its wager debit and optional payout credit, protected by a unique request token. Participant randomness is cryptographically seeded and independent of player data; simulation randomness is seeded and reproducible.

## Backup, restore, and reset

Stop the server before backup or restore. The default database is `instance/lucky_lab.db`.

```bash
cp instance/lucky_lab.db instance/lucky_lab.backup.db
cp instance/lucky_lab.backup.db instance/lucky_lab.db
.venv/bin/flask --app app:create_app main reset-demo-data
```

Reset removes participant, session, spin, ledger, and simulation data but retains teaching models. Export CSV files first if the classroom needs the records.

## Design and mathematics

The active definition uses five explicit cyclic reel strips, three visible rows, five paylines, and integer minor units (100 units = 1.00 displayed credit). The selected stake is total stake and divides evenly between lines. `app/game_engine.py` is framework-independent and supports seeded outcomes and exact enumeration.

The baseline’s theoretical RTP, hit rate, and variance are calculated by enumerating every reel-stop combination and stored with its canonical SHA-256 definition hash. Simulations record the seed, generator, model hash, configuration, uncertainty interval, and trial results. Simulation data never posts to participant ledgers.

The original product documents remain in `01_...md` through `08_...md`; supplied reference artwork and generation provenance are in `visuals/`. Production asset provenance is in `docs/ASSET_PROVENANCE.md`.

## Known limits

- Version 1 supports base-game paylines and extension points but no wild/scatter feature implementation.
- Simulation execution is synchronous; the configured 100,000-spin ceiling is suitable for local experiments, but the browser waits for completion.
- The model editor exposes validated JSON rather than a guided reel-strip/paytable builder.
- Charts use a small local canvas renderer with an accessible data disclosure; they are dependency-free.
- No authentication is present, by design.
