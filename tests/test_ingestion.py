from sqlalchemy import select

from app.db.models import Segment, Turn
from app.ingestion.loaders import ingest_file
from app.preprocessing.segmenters import preprocess_turns


def test_ingesting_demo_conversations(db_session):
    count = ingest_file(db_session, "data/raw/demo_conversations.csv", "csv")
    assert count == 5
    assert len(db_session.scalars(select(Turn)).all()) == 5


def test_segmenting_turns(db_session):
    ingest_file(db_session, "data/raw/demo_conversations.csv", "csv")
    count = preprocess_turns(db_session, strategy="turn")
    assert count == 5
    assert len(db_session.scalars(select(Segment)).all()) == 5
