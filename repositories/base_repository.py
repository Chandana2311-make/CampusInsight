"""
Base Repository
Provides standardized parameterized query execution, row-to-dict conversion, and error handling.
"""
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from database.connection import get_connection, get_db_context


class BaseRepository:
    """Base class for all data repositories."""
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = db_path

    def _dict_from_row(self, row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        """Converts an SQLite Row object to a standard Python dictionary."""
        if row is None:
            return None
        return dict(row)

    def _dicts_from_rows(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """Converts a list of SQLite Row objects to a list of dictionaries."""
        return [dict(row) for row in rows]

    def execute_query(
        self,
        query: str,
        params: Union[Tuple, List, Dict] = (),
        conn: Optional[sqlite3.Connection] = None
    ) -> List[Dict[str, Any]]:
        """Executes a SELECT query with parameters and returns a list of dictionaries."""
        if conn is not None:
            cursor = conn.execute(query, params)
            return self._dicts_from_rows(cursor.fetchall())
        
        with get_db_context(self.db_path) as active_conn:
            cursor = active_conn.execute(query, params)
            return self._dicts_from_rows(cursor.fetchall())

    def execute_query_one(
        self,
        query: str,
        params: Union[Tuple, List, Dict] = (),
        conn: Optional[sqlite3.Connection] = None
    ) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query expecting 0 or 1 row."""
        if conn is not None:
            cursor = conn.execute(query, params)
            return self._dict_from_row(cursor.fetchone())
            
        with get_db_context(self.db_path) as active_conn:
            cursor = active_conn.execute(query, params)
            return self._dict_from_row(cursor.fetchone())

    def execute_non_query(
        self,
        query: str,
        params: Union[Tuple, List, Dict] = (),
        conn: Optional[sqlite3.Connection] = None
    ) -> int:
        """
        Executes an INSERT, UPDATE, or DELETE query.
        Returns the lastrowid for INSERT or rowcount for UPDATE/DELETE.
        """
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        with get_db_context(self.db_path) as active_conn:
            cursor = active_conn.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
