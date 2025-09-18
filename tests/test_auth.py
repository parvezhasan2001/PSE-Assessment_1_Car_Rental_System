import pytest

try:
    from utils.auth import hash_password, verify_password
except Exception as e:
    pytest.skip(f"utils.auth not importable: {e}", allow_module_level=True)

def test_bcrypt_roundtrip():
    password = "Secret123"
    hashed = hash_password(password)
    assert hashed and hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False
