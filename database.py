from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from models import Base

settings = get_settings()


engine = create_engine(settings.database.get_url())
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    with Session() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
