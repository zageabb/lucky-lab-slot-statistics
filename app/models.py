from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(db.String(80))
    normalized_name: Mapped[str] = mapped_column(db.String(80), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    sessions: Mapped[list[PlaySession]] = relationship(back_populates="player")
    ledger_entries: Mapped[list[LedgerEntry]] = relationship(back_populates="player")


class GameModel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    description: Mapped[str] = mapped_column(db.Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    versions: Mapped[list[GameModelVersion]] = relationship(back_populates="game_model")


class GameModelVersion(db.Model):
    __table_args__ = (UniqueConstraint("game_model_id", "version_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    game_model_id: Mapped[int] = mapped_column(ForeignKey("game_model.id"))
    version_number: Mapped[int]
    status: Mapped[str] = mapped_column(db.String(20), default="draft")
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    definition_json: Mapped[dict] = mapped_column(db.JSON)
    definition_hash: Mapped[str] = mapped_column(db.String(64), unique=True)
    theoretical_rtp: Mapped[float | None]
    theoretical_hit_rate: Mapped[float | None]
    theoretical_variance: Mapped[float | None]
    calculation_method: Mapped[str] = mapped_column(db.String(30), default="exact")
    published_at: Mapped[datetime | None]
    game_model: Mapped[GameModel] = relationship(back_populates="versions")


class PlaySession(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"), index=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("game_model_version.id"))
    started_at: Mapped[datetime] = mapped_column(default=utcnow)
    ended_at: Mapped[datetime | None]
    player: Mapped[Player] = relationship(back_populates="sessions")
    spins: Mapped[list[Spin]] = relationship(back_populates="session")


class Spin(db.Model):
    __table_args__ = (
        CheckConstraint("stake_units > 0"),
        CheckConstraint("payout_units >= 0"),
        Index("ix_spin_session_created", "play_session_id", "created_at"),
    )
    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    request_token: Mapped[str] = mapped_column(db.String(64), unique=True)
    play_session_id: Mapped[int] = mapped_column(ForeignKey("play_session.id"))
    model_version_id: Mapped[int] = mapped_column(ForeignKey("game_model_version.id"))
    stake_units: Mapped[int]
    payout_units: Mapped[int]
    board_json: Mapped[list] = mapped_column(db.JSON)
    evaluation_json: Mapped[dict] = mapped_column(db.JSON)
    feature_state_json: Mapped[dict] = mapped_column(db.JSON, default=dict)
    rng_audit_hash: Mapped[str] = mapped_column(db.String(64))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    session: Mapped[PlaySession] = relationship(back_populates="spins")


class LedgerEntry(db.Model):
    __table_args__ = (CheckConstraint("entry_type in ('ALLOCATION','WAGER','PAYOUT','ADJUSTMENT','RESET')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"), index=True)
    spin_id: Mapped[str | None] = mapped_column(ForeignKey("spin.id"), index=True)
    entry_type: Mapped[str] = mapped_column(db.String(20))
    amount_units: Mapped[int]
    balance_after_units: Mapped[int]
    note: Mapped[str] = mapped_column(db.String(240), default="")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    player: Mapped[Player] = relationship(back_populates="ledger_entries")


class SimulationRun(db.Model):
    id: Mapped[str] = mapped_column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    model_version_id: Mapped[int] = mapped_column(ForeignKey("game_model_version.id"))
    status: Mapped[str] = mapped_column(db.String(20), default="completed")
    seed: Mapped[int]
    requested_spins: Mapped[int]
    configuration_json: Mapped[dict] = mapped_column(db.JSON)
    summary_json: Mapped[dict] = mapped_column(db.JSON)
    started_at: Mapped[datetime] = mapped_column(default=utcnow)
    completed_at: Mapped[datetime | None]
    trials: Mapped[list[SimulationTrial]] = relationship(cascade="all, delete-orphan")


class SimulationTrial(db.Model):
    __table_args__ = (UniqueConstraint("simulation_run_id", "trial_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_run_id: Mapped[str] = mapped_column(ForeignKey("simulation_run.id"), index=True)
    trial_number: Mapped[int]
    spins_completed: Mapped[int]
    total_wager_units: Mapped[int]
    total_payout_units: Mapped[int]
    ending_balance_units: Mapped[int]
    max_drawdown_units: Mapped[int]
    longest_losing_streak: Mapped[int]
    summary_json: Mapped[dict] = mapped_column(db.JSON)
