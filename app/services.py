from __future__ import annotations

import hashlib
import random
import secrets
from datetime import datetime, timezone
from statistics import fmean, median, pvariance

from sqlalchemy import func, select

from .extensions import db
from .game_engine import ModelDefinition, confidence_interval, exact_statistics, spin
from .models import GameModelVersion, LedgerEntry, PlaySession, Player, SimulationRun, SimulationTrial, Spin


def balance_units(player_id: int) -> int:
    return db.session.scalar(select(func.coalesce(func.sum(LedgerEntry.amount_units), 0)).where(LedgerEntry.player_id == player_id)) or 0


def player_metrics(player_id: int) -> dict:
    entries = db.session.scalars(select(LedgerEntry).where(LedgerEntry.player_id == player_id).order_by(LedgerEntry.id)).all()
    sessions = db.session.scalars(select(PlaySession.id).where(PlaySession.player_id == player_id)).all()
    spins = db.session.scalars(select(Spin).where(Spin.play_session_id.in_(sessions)).order_by(Spin.created_at)).all() if sessions else []
    allocated = sum(e.amount_units for e in entries if e.entry_type == "ALLOCATION" and e.amount_units > 0)
    wagered = -sum(e.amount_units for e in entries if e.entry_type == "WAGER")
    payout = sum(e.amount_units for e in entries if e.entry_type == "PAYOUT")
    hit_count = sum(s.payout_units > 0 for s in spins)
    be_count = sum(s.payout_units >= s.stake_units for s in spins)
    profit_count = sum(s.payout_units > s.stake_units for s in spins)
    longest_loss = current = longest_zero = current_zero = 0
    bankroll = []
    for s in spins:
        current = current + 1 if s.payout_units < s.stake_units else 0
        current_zero = current_zero + 1 if s.payout_units == 0 else 0
        longest_loss, longest_zero = max(longest_loss, current), max(longest_zero, current_zero)
    for e in entries:
        if e.spin_id:
            bankroll.append(e.balance_after_units / 100)
    count = len(spins)
    return {"allocated": allocated, "balance": sum(e.amount_units for e in entries), "wagered": wagered, "payout": payout,
            "net": payout - wagered, "spins": count, "rtp": payout / wagered if wagered else None,
            "hit_rate": hit_count / count if count else None, "break_even_rate": be_count / count if count else None,
            "profitable_rate": profit_count / count if count else None, "longest_loss": longest_loss,
            "longest_zero": longest_zero, "bankroll": bankroll}


def allocate(player: Player, amount_units: int, note: str = "Classroom allocation") -> LedgerEntry:
    if amount_units <= 0:
        raise ValueError("allocation must be positive")
    entry = LedgerEntry(player_id=player.id, entry_type="ALLOCATION", amount_units=amount_units,
                        balance_after_units=balance_units(player.id) + amount_units, note=note)
    db.session.add(entry)
    db.session.commit()
    return entry


def play_spin(session: PlaySession, stake_units: int, request_token: str) -> Spin:
    replay = db.session.scalar(select(Spin).where(Spin.request_token == request_token))
    if replay:
        return replay
    if session.ended_at:
        raise ValueError("session has ended")
    version = db.session.get(GameModelVersion, session.model_version_id)
    if not version or version.status != "published":
        raise ValueError("session model is not published")
    model = ModelDefinition.model_validate(version.definition_json)
    if stake_units not in model.allowed_stakes:
        raise ValueError("stake is not allowed")
    before = balance_units(session.player_id)
    if before < stake_units:
        raise ValueError("insufficient virtual credits")
    rng_seed = secrets.token_bytes(32)
    result = spin(model, stake_units, random.Random(int.from_bytes(rng_seed)))
    audit_hash = hashlib.sha256(rng_seed + request_token.encode()).hexdigest()
    row = Spin(request_token=request_token, play_session_id=session.id, model_version_id=version.id,
               stake_units=stake_units, payout_units=result.payout_units, board_json=result.board,
               evaluation_json={"stops": result.stops, "line_awards": result.line_awards},
               feature_state_json={}, rng_audit_hash=audit_hash)
    db.session.add(row)
    db.session.flush()
    db.session.add(LedgerEntry(player_id=session.player_id, spin_id=row.id, entry_type="WAGER",
                               amount_units=-stake_units, balance_after_units=before-stake_units, note="Spin wager"))
    if result.payout_units:
        db.session.add(LedgerEntry(player_id=session.player_id, spin_id=row.id, entry_type="PAYOUT",
                                   amount_units=result.payout_units, balance_after_units=before-stake_units+result.payout_units,
                                   note="Evaluated line payout"))
    db.session.commit()
    return row


def run_simulation(version: GameModelVersion, seed: int, spins: int, trials: int, bankroll: int, stake: int, stop_at_zero: bool) -> SimulationRun:
    if spins < 1 or spins > 100_000 or trials < 1 or trials > 500:
        raise ValueError("simulation size is outside classroom limits")
    model = ModelDefinition.model_validate(version.definition_json)
    if stake not in model.allowed_stakes:
        raise ValueError("stake is not allowed by this model")
    run = SimulationRun(model_version_id=version.id, seed=seed, requested_spins=spins,
                        configuration_json={"seed": seed, "spins": spins, "trials": trials, "starting_bankroll_units": bankroll,
                                            "stake_units": stake, "stop_at_zero": stop_at_zero, "generator": "random.Random/MT19937",
                                            "model_hash": version.definition_hash}, summary_json={})
    db.session.add(run); db.session.flush()
    rtps, endings, all_returns, ruined, hit_total, spin_total = [], [], [], 0, 0, 0
    first_path: list[float] = []
    for t in range(trials):
        rng = random.Random(seed + t)
        cash = bankroll; peak = cash; max_drawdown = 0; loss = longest = 0; paid = 0; count = 0
        returns: list[float] = []
        for _ in range(spins):
            if stop_at_zero and cash < stake: break
            outcome = spin(model, stake, rng); cash += outcome.payout_units - stake; paid += outcome.payout_units; count += 1
            value = outcome.payout_units / stake; returns.append(value); all_returns.append(value)
            hit_total += outcome.payout_units > 0; spin_total += 1
            loss = loss + 1 if outcome.payout_units < stake else 0; longest = max(longest, loss)
            peak = max(peak, cash); max_drawdown = max(max_drawdown, peak-cash)
            if t == 0 and (count <= 200 or count % max(1, spins//200) == 0): first_path.append(cash/100)
        ruined += cash < stake; endings.append(cash); rtps.append(paid/(count*stake) if count else 0)
        db.session.add(SimulationTrial(simulation_run_id=run.id, trial_number=t+1, spins_completed=count,
                       total_wager_units=count*stake, total_payout_units=paid, ending_balance_units=cash,
                       max_drawdown_units=max_drawdown, longest_losing_streak=longest, summary_json={"rtp": rtps[-1]}))
    low, high = confidence_interval(all_returns)
    run.summary_json = {"observed_rtp": fmean(rtps), "median_rtp": median(rtps), "return_variance": pvariance(all_returns) if len(all_returns)>1 else 0,
                        "hit_rate": hit_total/spin_total if spin_total else 0, "risk_of_ruin": ruined/trials,
                        "mean_ending_units": fmean(endings), "min_ending_units": min(endings), "max_ending_units": max(endings),
                        "confidence_low": low, "confidence_high": high, "completed_spins": spin_total,
                        "bankroll_path": first_path, "ending_balances": [e/100 for e in endings], "trial_rtps": rtps}
    run.completed_at = datetime.now(timezone.utc); db.session.commit(); return run


def publish_version(version: GameModelVersion) -> None:
    if version.status != "draft": raise ValueError("only drafts can be published")
    definition = ModelDefinition.model_validate(version.definition_json)
    stats = exact_statistics(definition)
    version.definition_hash = definition.canonical_hash(); version.theoretical_rtp = stats["rtp"]
    version.theoretical_hit_rate = stats["hit_rate"]; version.theoretical_variance = stats["variance"]
    version.calculation_method = "exact"; version.status = "published"; version.published_at = datetime.now(timezone.utc)
    db.session.commit()
