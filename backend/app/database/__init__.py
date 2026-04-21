"""Database modules"""
from app.database.oracle import oracle_db
from app.database.postgres import postgres_db
from app.database.jposee import JposEEDB

# Initialize jPOS EE database instance
jposee_db = JposEEDB()

__all__ = ["oracle_db", "postgres_db", "jposee_db"]

