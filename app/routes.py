from __future__ import annotations

import csv
import io
import json
from uuid import uuid4

from flask import Blueprint, Response, abort, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import select

from .baseline import BASELINE
from .extensions import db
from .game_engine import ModelDefinition
from .models import GameModel, GameModelVersion, LedgerEntry, PlaySession, Player, SimulationRun, SimulationTrial, Spin
from .services import allocate, balance_units, play_spin, player_metrics, publish_version, run_simulation

bp = Blueprint("main", __name__)


@bp.app_template_filter("credits")
def credits(value): return f"{(value or 0)/100:,.2f}"


@bp.app_template_filter("pct")
def pct(value): return "—" if value is None else f"{value*100:.2f}%"


def active_version() -> GameModelVersion:
    version = db.session.scalar(select(GameModelVersion).where(GameModelVersion.is_active.is_(True)))
    if not version: abort(503, "No active probability model. Run flask seed.")
    return version


@bp.get("/")
def home():
    return render_template("home.html", players=db.session.scalars(select(Player).order_by(Player.display_name)).all(),
                           model=active_version(), runs=db.session.scalars(select(SimulationRun).order_by(SimulationRun.started_at.desc()).limit(3)).all())


@bp.get("/health")
def health(): return {"status": "ok", "scope": "local classroom", "money": False}


@bp.post("/players")
def create_player():
    name = request.form.get("display_name", "").strip()
    if not name: flash("Enter a display name.", "error"); return redirect(url_for("main.home"))
    normalized = " ".join(name.casefold().split())
    player = db.session.scalar(select(Player).where(Player.normalized_name == normalized))
    if player: flash("That player already exists; selected the existing record.", "info"); return redirect(url_for("main.player", player_id=player.id))
    player = Player(display_name=name, normalized_name=normalized); db.session.add(player); db.session.commit()
    amount = int(request.form.get("allocation", "10000"))
    allocate(player, amount)
    return redirect(url_for("main.player", player_id=player.id))


@bp.get("/players/<int:player_id>")
def player(player_id):
    player = db.get_or_404(Player, player_id); metrics = player_metrics(player_id)
    sessions = db.session.scalars(select(PlaySession).where(PlaySession.player_id == player_id).order_by(PlaySession.started_at.desc())).all()
    session = next((s for s in sessions if not s.ended_at), None)
    spins = db.session.scalars(select(Spin).where(Spin.play_session_id.in_([s.id for s in sessions])).order_by(Spin.created_at.desc()).limit(10)).all() if sessions else []
    winning_lines = [line for line in spins[0].evaluation_json["line_awards"] if line["payout_units"] > 0] if spins else []
    winning_cells = {(row, col) for line in winning_lines for col, row in enumerate(line["rows"][:line["matches"]])}
    return render_template("player.html", player=player, metrics=metrics, session=session, sessions=sessions,
                           spins=spins, winning_lines=winning_lines, winning_cells=winning_cells,
                           model=active_version(), token=str(uuid4()))


@bp.get("/players/<int:player_id>/statistics")
def player_statistics(player_id):
    player = db.get_or_404(Player, player_id)
    sessions = db.session.scalars(select(PlaySession).where(PlaySession.player_id == player_id).order_by(PlaySession.started_at.desc())).all()
    entries = db.session.scalars(select(LedgerEntry).where(LedgerEntry.player_id == player_id).order_by(LedgerEntry.id.desc()).limit(100)).all()
    spins = db.session.scalars(select(Spin).where(Spin.play_session_id.in_([s.id for s in sessions])).order_by(Spin.created_at.desc()).limit(20)).all() if sessions else []
    return render_template("player_statistics.html", player=player, metrics=player_metrics(player_id),
                           sessions=sessions, entries=entries, spins=spins, model=active_version())


@bp.post("/players/<int:player_id>/allocate")
def add_allocation(player_id):
    allocate(db.get_or_404(Player, player_id), int(request.form["amount_units"])); flash("Virtual credits allocated.", "success")
    return redirect(url_for("main.player", player_id=player_id))


@bp.post("/players/<int:player_id>/sessions")
def start_session(player_id):
    player = db.get_or_404(Player, player_id)
    existing = db.session.scalar(select(PlaySession).where(PlaySession.player_id == player.id, PlaySession.ended_at.is_(None)))
    if not existing:
        db.session.add(PlaySession(player_id=player.id, model_version_id=active_version().id)); db.session.commit()
    return redirect(url_for("main.player", player_id=player_id))


@bp.post("/sessions/<int:session_id>/spin")
def do_spin(session_id):
    session = db.get_or_404(PlaySession, session_id)
    try:
        row = play_spin(session, int(request.form["stake_units"]), request.form["request_token"])
        if request.headers.get("X-Requested-With") == "LuckyLabDrums":
            metrics = player_metrics(session.player_id)
            return jsonify({"ok": True, "spin_id": row.id, "board": row.board_json,
                            "stake_units": row.stake_units, "payout_units": row.payout_units,
                            "balance_units": metrics["balance"],
                            "line_awards": row.evaluation_json["line_awards"],
                            "audit_url": url_for("main.spin_audit", spin_id=row.id)})
    except ValueError as exc:
        if request.headers.get("X-Requested-With") == "LuckyLabDrums":
            return jsonify({"ok": False, "error": str(exc)}), 400
        flash(str(exc), "error")
    return redirect(url_for("main.player", player_id=session.player_id))


@bp.get("/spins/<spin_id>")
def spin_audit(spin_id): return render_template("spin.html", spin=db.get_or_404(Spin, spin_id))


@bp.get("/models")
def models(): return render_template("models.html", versions=db.session.scalars(select(GameModelVersion).order_by(GameModelVersion.id)).all())


@bp.post("/models/<int:version_id>/clone")
def clone_model(version_id):
    source = db.get_or_404(GameModelVersion, version_id); number = max(v.version_number for v in source.game_model.versions)+1
    draft = GameModelVersion(game_model_id=source.game_model_id, version_number=number, status="draft",
                             definition_json=source.definition_json, definition_hash=f"draft-{uuid4()}")
    db.session.add(draft); db.session.commit(); return redirect(url_for("main.edit_model", version_id=draft.id))


@bp.route("/models/<int:version_id>/edit", methods=["GET", "POST"])
def edit_model(version_id):
    version = db.get_or_404(GameModelVersion, version_id)
    if version.status != "draft": abort(409, "Published versions are immutable")
    if request.method == "POST":
        try:
            definition = ModelDefinition.model_validate_json(request.form["definition_json"])
            version.definition_json = definition.model_dump(); version.definition_hash = f"draft-{uuid4()}"; db.session.commit(); flash("Draft validated and saved.", "success")
        except Exception as exc: flash(f"Validation failed: {exc}", "error")
    return render_template("model_edit.html", version=version, definition=json.dumps(version.definition_json, indent=2))


@bp.post("/models/<int:version_id>/publish")
def publish_model(version_id):
    version = db.get_or_404(GameModelVersion, version_id)
    try: publish_version(version); flash("Model published with exact calculated statistics.", "success")
    except ValueError as exc: flash(str(exc), "error")
    return redirect(url_for("main.models"))


@bp.post("/models/<int:version_id>/activate")
def activate_model(version_id):
    version = db.get_or_404(GameModelVersion, version_id)
    if version.status != "published": abort(409)
    for item in db.session.scalars(select(GameModelVersion).where(GameModelVersion.is_active.is_(True))): item.is_active = False
    version.is_active = True; db.session.commit(); flash("Active participant model changed. Historical spins are unchanged.", "success")
    return redirect(url_for("main.models"))


@bp.route("/simulations", methods=["GET", "POST"])
def simulations():
    versions = db.session.scalars(select(GameModelVersion).where(GameModelVersion.status == "published")).all()
    if request.method == "POST":
        version = db.get_or_404(GameModelVersion, int(request.form["model_version_id"]))
        try:
            run = run_simulation(version, int(request.form["seed"]), int(request.form["spins"]), int(request.form["trials"]),
                                 int(request.form["bankroll_units"]), int(request.form["stake_units"]), request.form.get("stop_at_zero") == "on")
            return redirect(url_for("main.simulation", run_id=run.id))
        except ValueError as exc: flash(str(exc), "error")
    runs = db.session.scalars(select(SimulationRun).order_by(SimulationRun.started_at.desc()).limit(20)).all()
    return render_template("simulations.html", versions=versions, runs=runs)


@bp.get("/simulations/<run_id>")
def simulation(run_id): return render_template("simulation.html", run=db.get_or_404(SimulationRun, run_id))


@bp.get("/learn")
def learn(): return render_template("learn.html")


@bp.get("/model-manual")
def model_manual(): return render_template("model_manual.html")


@bp.get("/exports/players/<int:player_id>/ledger.csv")
def ledger_csv(player_id):
    rows = db.session.scalars(select(LedgerEntry).where(LedgerEntry.player_id == player_id).order_by(LedgerEntry.id)).all()
    output=io.StringIO(); writer=csv.writer(output); writer.writerow(["id","timestamp_utc","type","amount_units","balance_after_units","spin_id","note"])
    for e in rows: writer.writerow([e.id,e.created_at.isoformat(),e.entry_type,e.amount_units,e.balance_after_units,e.spin_id or "",e.note])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename=player-{player_id}-ledger.csv"})


@bp.get("/exports/simulations/<run_id>.csv")
def simulation_csv(run_id):
    run=db.get_or_404(SimulationRun, run_id); output=io.StringIO(); writer=csv.writer(output)
    writer.writerow(["configuration", json.dumps(run.configuration_json, sort_keys=True)]); writer.writerow(["summary", json.dumps(run.summary_json, sort_keys=True)])
    writer.writerow(["trial","spins","wager_units","payout_units","ending_units","max_drawdown_units","longest_losing_streak"])
    for t in run.trials: writer.writerow([t.trial_number,t.spins_completed,t.total_wager_units,t.total_payout_units,t.ending_balance_units,t.max_drawdown_units,t.longest_losing_streak])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename=simulation-{run.id}.csv"})


@bp.cli.command("seed")
def seed_command():
    if db.session.scalar(select(GameModelVersion)): print("Models already seeded"); return
    model=GameModel(name="Meadow", description="Original transparent five-reel classroom model")
    db.session.add(model); db.session.flush()
    version=GameModelVersion(game_model_id=model.id, version_number=1, status="draft", definition_json=BASELINE.model_dump(), definition_hash=f"draft-{uuid4()}")
    db.session.add(version); db.session.commit(); publish_version(version); version.is_active=True; db.session.commit()
    print(f"Seeded Meadow v1; exact RTP {version.theoretical_rtp:.4%}")


@bp.cli.command("reset-demo-data")
def reset_demo_data_command():
    """Remove participant and simulation data; retain published teaching models."""
    for model in (LedgerEntry, Spin, PlaySession, Player, SimulationTrial, SimulationRun):
        db.session.execute(model.__table__.delete())
    db.session.commit()
    print("Participant, ledger, spin, session, and simulation data reset; models retained.")
