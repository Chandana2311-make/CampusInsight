"""
Authentication and Authorization Service
Implements PBKDF2 password hashing with salt, user verification, and permission validation.
"""
import hashlib
import hmac
import os
from typing import Any, Dict, Optional, Tuple
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository


class AuthService:
    """Service handling password cryptography, user authentication, and profile lookups."""

    def __init__(self, user_repo: Optional[UserRepository] = None, student_repo: Optional[StudentRepository] = None):
        self.user_repo = user_repo or UserRepository()
        self.student_repo = student_repo or StudentRepository()

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
        Returns a tuple of (hex_hash, hex_salt).
        """
        if not salt:
            salt_bytes = os.urandom(16)
            salt = salt_bytes.hex()
        else:
            salt_bytes = bytes.fromhex(salt)

        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=salt_bytes,
            iterations=100_000
        )
        return key.hex(), salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verifies a plaintext password against the stored hash and salt."""
        computed_hash, _ = AuthService.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)

    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        full_name: str,
        email: str
    ) -> int:
        """Registers a new user account with hashed password."""
        if not username or not password or not role or not full_name or not email:
            raise ValueError("All user fields are required.")
        if role not in ("student", "faculty", "admin"):
            raise ValueError(f"Invalid role: {role}")
            
        existing = self.user_repo.get_by_username(username)
        if existing:
            raise ValueError(f"Username '{username}' already exists.")

        pwd_hash, salt = self.hash_password(password)
        return self.user_repo.create_user(
            username=username,
            password_hash=pwd_hash,
            salt=salt,
            role=role,
            full_name=full_name,
            email=email
        )

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates credentials and returns sanitized user session data.
        Returns None on failed authentication.
        """
        if not username or not password:
            return None

        user = self.user_repo.get_by_username(username)
        if not user:
            return None

        if not self.verify_password(password, user["password_hash"], user["salt"]):
            return None

        # Sanitize sensitive fields before returning
        safe_user = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
            "email": user["email"],
            "created_at": user["created_at"]
        }

        # If student, attach student profile
        if user["role"] == "student":
            student_profile = self.student_repo.get_by_user_id(user["id"])
            if student_profile:
                safe_user["student_id"] = student_profile["id"]
                safe_user["usn"] = student_profile["usn"]
                safe_user["branch"] = student_profile["branch"]
                safe_user["semester"] = student_profile["semester"]
                safe_user["section"] = student_profile["section"]

        return safe_user
