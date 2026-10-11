"""
Database Initialization Module
Applies database schema and verifies table integrity.
"""
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from typing import Optional, Union
from database.connection import get_connection, get_db_context
from config import BASE_DIR, DATABASE_PATH


def init_database(db_path: Optional[Union[str, Path]] = None) -> None:
    """
    Initializes the SQLite database with the full schema.
    """
    schema_path = BASE_DIR / "database" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with get_db_context(db_path) as conn:
        conn.executescript(schema_sql)


def reset_database(db_path: Optional[Union[str, Path]] = None) -> None:
    """
    Drops and recreates all database tables. (Useful for tests and resetting demo state).
    """
    target = Path(db_path) if db_path else DATABASE_PATH
    if target.exists():
        target.unlink(missing_ok=True)
    init_database(target)


if __name__ == "__main__":
    print(f"Initializing database at: {DATABASE_PATH}")
    init_database()
    print("Database initialization completed successfully.")
