from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.

    Raises:
        UnknownHashError: If an error occurs during password hashing.
        ValueError: If the password is empty or invalid.
    """
    # Validate input
    if not password:
        raise ValueError("Password cannot be empty")

    # Hash the password
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.

    Raises:
        UnknownHashError: If the hashed password format is invalid.
        ValueError: If the plain password or hashed password is empty or invalid.
    """
    # Validate inputs
    if not plain_password or not hashed_password:
        raise ValueError("Password or hashed password cannot be empty")

    # Verify the password
    return pwd_context.verify(plain_password, hashed_password)