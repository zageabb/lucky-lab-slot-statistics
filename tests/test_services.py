from sqlalchemy import select

from app.baseline import BASELINE
from app.extensions import db
from app.models import GameModel, GameModelVersion, LedgerEntry, PlaySession, Player, SimulationTrial
from app.services import allocate, balance_units, play_spin, publish_version, run_simulation


def setup_player():
    model=GameModel(name="Test"); db.session.add(model); db.session.flush()
    version=GameModelVersion(game_model_id=model.id, version_number=1, status="draft", definition_json=BASELINE.model_dump(), definition_hash="draft")
    player=Player(display_name="Student A", normalized_name="student a"); db.session.add_all([version,player]); db.session.commit(); publish_version(version); version.is_active=True
    allocate(player,10000); session=PlaySession(player_id=player.id,model_version_id=version.id); db.session.add(session); db.session.commit()
    return player,session,version


def test_ledger_allocation_and_spin_idempotency(app):
    with app.app_context():
        player,session,_=setup_player(); first=play_spin(session,100,"same-token"); second=play_spin(session,100,"same-token")
        assert first.id==second.id
        entries=db.session.scalars(select(LedgerEntry).where(LedgerEntry.player_id==player.id)).all()
        assert sum(e.amount_units for e in entries)==balance_units(player.id)
        assert len([e for e in entries if e.entry_type=="WAGER"])==1


def test_simulation_is_reproducible_and_separate(app):
    with app.app_context():
        player,_,version=setup_player(); before=balance_units(player.id)
        one=run_simulation(version,123,100,2,10000,100,True)
        summary=one.summary_json.copy(); two=run_simulation(version,123,100,2,10000,100,True)
        assert summary==two.summary_json
        assert balance_units(player.id)==before
        assert db.session.scalar(select(SimulationTrial).where(SimulationTrial.simulation_run_id==one.id))
