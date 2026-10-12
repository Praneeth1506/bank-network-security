import os
import tempfile

# Must be set before app.main is imported so the engine never points at banknet.db.
_tmpdir = tempfile.mkdtemp(prefix="banknet-test-")
os.environ["BANKNET_DB_URL"] = f"sqlite:///{os.path.join(_tmpdir, 'test.db')}"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.main import app, engine


@pytest.fixture
def client():
    SQLModel.metadata.drop_all(engine)
    with TestClient(app) as c:      # lifespan runs create_all
        yield c
