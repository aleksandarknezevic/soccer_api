import os
import tempfile
import pytest
from app.main.factory import create_app


@pytest.fixture(scope='module')
def test_client():
    db_fd, db_path = tempfile.mkstemp()
    application = create_app(db_path)
    testing_client = application.test_client()

    ctx = application.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    os.close(db_fd)
    os.unlink(db_path)
