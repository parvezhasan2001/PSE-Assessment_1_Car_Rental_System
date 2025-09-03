import re

def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    # at least 6 characters, one uppercase, one digit
    return bool(re.match(r'^(?=.*[A-Z])(?=.*\d).{6,}$', password))

def validate_username(username: str) -> bool:
    return len(username) >= 3
