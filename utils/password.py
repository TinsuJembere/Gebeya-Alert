"""
Password hashing and verification utilities.

This module implements secure password hashing using SHA-256 pre-hashing
followed by bcrypt. This approach removes bcrypt's 72-byte limit while
maintaining security.

Process:
1. Hash password with SHA-256 (produces 64-byte hex string)
2. Hash the SHA-256 digest with bcrypt

This ensures:
- No password length restrictions
- Backward compatibility with existing bcrypt hashes
- Strong security (SHA-256 + bcrypt)
"""
import hashlib
import bcrypt

# Try to use passlib, but fall back to bcrypt directly if there are issues
try:
    from passlib.context import CryptContext
    _use_passlib = True
    # Initialize passlib context for bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    _use_passlib = False
    pwd_context = None


def _pre_hash_password(password: str) -> bytes:
    """
    Pre-hash password using SHA-256 to remove bcrypt's 72-byte limit.
    
    Args:
        password: Plain text password (any length)
        
    Returns:
        SHA-256 digest as bytes (32 bytes, always fits in 72-byte limit)
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 pre-hashing + bcrypt.
    
    This function:
    1. First hashes the password with SHA-256 (removes length limit)
    2. Then hashes the SHA-256 digest with bcrypt (secure storage)
    
    Args:
        password: Plain text password (any length, no truncation)
        
    Returns:
        Hashed password string (bcrypt hash of SHA-256 digest)
        
    Note:
        - No password length restrictions
        - Backward compatible: verify_password() can still verify old bcrypt hashes
        - All passwords are now stored as: bcrypt(SHA256(password))
    """
    # Pre-hash with SHA-256 to remove bcrypt's 72-byte limit
    # SHA-256 produces 32 bytes (well within bcrypt's 72-byte limit)
    sha256_digest = _pre_hash_password(password)
    
    # Hash the SHA-256 digest with bcrypt
    # Use bcrypt directly to avoid passlib initialization issues
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sha256_digest, salt)
    
    # Return as string (bcrypt hash is already a string when decoded)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    This function supports:
    1. New format: bcrypt(SHA256(password)) - verifies by pre-hashing and checking
    2. Old format: bcrypt(password) - backward compatibility for existing users
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Note:
        - Automatically handles both new (SHA-256 pre-hashed) and old (direct bcrypt) formats
        - Backward compatible with existing password hashes
    """
    if not hashed_password:
        return False
    
    try:
        # Try new format first: bcrypt(SHA256(password))
        sha256_digest = _pre_hash_password(plain_password)
        hashed_bytes = hashed_password.encode("utf-8")
        
        # Verify using the SHA-256 digest
        if bcrypt.checkpw(sha256_digest, hashed_bytes):
            return True
    except Exception:
        # If verification fails, try old format
        pass
    
    # Backward compatibility: try old format (direct bcrypt)
    # This allows existing users with old password hashes to still login
    # Note: This check is safe because bcrypt hashes have a specific format
    # and won't accidentally match a SHA-256 pre-hashed password
    try:
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        
        # Only try if password is <= 72 bytes (old format limitation)
        if len(plain_bytes) <= 72:
            if bcrypt.checkpw(plain_bytes, hashed_bytes):
                return True
    except Exception:
        # If verification fails, password doesn't match
        pass
    
    return False
