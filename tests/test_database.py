from sqlalchemy import select

from app.db.models import Conversation


def test_database_initialization(db_session):
    db_session.add(Conversation(external_id="c1", title="Test", source="test", metadata_json=None))
    db_session.flush()
    assert db_session.scalar(select(Conversation).where(Conversation.external_id == "c1")) is not None
