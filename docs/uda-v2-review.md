# Lucky Lab — UDA V2 review and blockers (DEV-020)

**Review-only draft. Production activation MUST remain disabled.**

Verified against the repository's `compose.yaml`, `Dockerfile`,
`docker-entrypoint.sh`, `pyproject.toml` and `README.md`.

- One container `lucky-lab`, Flask/Gunicorn, container TCP port 5020,
  `/health` probe; source Compose currently publishes host port 5020
  without the proposed V2 loopback restriction.
- Container image built from `Dockerfile` using Python 3.12.
  V2 requires pinned Git source for the build, not an unpinned image.
- Local persistent bind `server-data:/data` contains SQLite
  `lucky_lab.db`; volume must be preserved and backed up before change.
- `SECRET_KEY` is secret-backed, while `DATABASE_URL` is defined
  by Compose as `sqlite:////data/lucky_lab.db`. Manifest names only;
  never copy the secret value.
- App has no internal login, according to README. UDA/Caddy authorization
  must protect all public routes. LAN port exposure must be reconciled.
- **Source-level startup split prepared (not production-activated):**
  `docker-entrypoint.sh` now starts Gunicorn **without** invoking
  `flask db upgrade` or `flask main seed`. Both are separated into
  `scripts/lucky-lab-db-maintenance.sh upgrade|seed`, which refuses
  execution unless explicit approval, verified-backup and database-target
  confirmation flags are supplied and `DATABASE_URL` is set.
  These flags are safety interlocks, NOT authentic approval or evidence
  that a backup/restore has been tested. Never infer migration/seed
  idempotency or run on live data without a reviewed change ticket.
  Dockerfile packages the maintenance script separately. Existing
  production images and data are unchanged.
- SQLite writes require explicit `database-write` capability; currently
  disabled by default and subject to production owner review.

## Unresolved acceptance gates

- [ ] Validate manifest against current canonical V2 schema and semantic checker.
- [ ] Inspect effective host container config, Docker volumes, ports,
      Caddy routes and UDA registry read-only via Desktop.
- [x] Separate source-level web entrypoint from DB upgrade/seed; preserve
      production activation hold pending database-owner confirmation.
- [ ] Verify genuine external approval and backup/restore evidence; startup
      interlock flags alone cannot establish authorisation.
- [ ] Verify live database path, backup ownership and restore procedure.
- [ ] Confirm required secret names, runtime effective health, UDA group
      and route with the authorised operator.
- [ ] Execute isolated build/test with disposable data and verify source SHA.
- [ ] Obtain separate production and database-write owner approvals.

The draft source entrypoint and Docker packaging have changed to remove
implicit database actions. Do not change live Compose, deployed entrypoints,
data volumes or running application as part of this review. No deployment,
database action or recovery is authorised.

## Independent regression evidence (20 November 2026)

Five no-network, no-database subprocess tests in
`tests/test_uda_db_lifecycle.py` were reconstructed from the committed
shell scripts and run in a disposable directory using fake `gunicorn`/
`flask` executables: **5 passed, 0 failed**; `sh -n` of the two scripts
also passed. The real Flask/SQLite migration, Docker image build,
production host and persistent data were NOT exercised.

Production readiness still requires the real image to be built/tested in
an isolated staging container with fresh disposable SQLite, explicit
versioned migration plans, a *verified* backup/restore, documented data
owner sign-off and read-only reconciliation of existing volume/ports/auth.
