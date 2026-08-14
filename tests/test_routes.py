from app.extensions import db
from app.models import GameModel, GameModelVersion
from app.baseline import BASELINE
from app.services import publish_version


def seed(app):
    with app.app_context():
        m=GameModel(name="Meadow"); db.session.add(m); db.session.flush()
        v=GameModelVersion(game_model_id=m.id,version_number=1,status="draft",definition_json=BASELINE.model_dump(),definition_hash="route-draft")
        db.session.add(v);db.session.commit();publish_version(v);v.is_active=True;db.session.commit()


def test_health(client):
    assert client.get('/health').json['money'] is False


def test_model_manual_renders(client):
    response = client.get('/model-manual')
    assert response.status_code == 200
    assert b'Probability model manual' in response.data
    assert b'allowed_stakes' in response.data


def test_create_player_duplicate_is_case_insensitive(app,client):
    seed(app)
    first=client.post('/players',data={'display_name':' Student A ','allocation':'10000'})
    second=client.post('/players',data={'display_name':'student a','allocation':'10000'})
    assert first.status_code==302 and second.status_code==302
