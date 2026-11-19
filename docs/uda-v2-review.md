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
- **CRITICAL:** current `docker-entrypoint.sh` runs `flask db upgrade`
  and `flask main seed` on every container start, before starting Gunicorn.
  V2 cannot safely activate this unmodified image just because the manifest
  is valid. Separate migration and seeding into explicit, versioned,
  approved operations. Verify backups and rollback/recovery; do not infer
  either command's idempotency.
- SQLite writes require explicit `database-write` capability; currently
  disabled by default and subject to production owner review.

## Unresolved acceptance gates

- [ ] Validate manifest against current canonical V2 schema and semantic checker.
- [ ] Inspect effective host container config, Docker volumes, ports,
      Caddy routes and UDA registry read-only via Desktop.
- [ ] Design safe migration/seeding split before attempting any container start.
- [ ] Verify live database path, backup ownership and restore procedure.
- [ ] Confirm required secret names, runtime effective health, UDA group
      and route with the authorised operator.
- [ ] Execute isolated build/test with disposable data and verify source SHA.
- [ ] Obtain separate production and database-write owner approvals.

Do not change Compose, runtime entrypoint, data volumes or live application
in this draft. No deployment or recovery is authorised.
