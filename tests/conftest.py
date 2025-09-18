import os
import tempfile
import shutil
import pytest

try:
    from dotenv import load_dotenv
    load_dotenv(".env.test")
except Exception:
    pass

@pytest.fixture(scope="session")
def temp_qr_dir():
    d = tempfile.mkdtemp(prefix="qr_")
    os.environ.setdefault("TEST_QR_DIR", d)
    yield d
    shutil.rmtree(d, ignore_errors=True)
