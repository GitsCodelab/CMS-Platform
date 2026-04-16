import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from config import settings

class PostgresDB:
    def __init__(self):
        self.host = settings.POSTGRES_HOST
        self.port = settings.POSTGRES_PORT
        self.user = settings.POSTGRES_USER
        self.password = settings.POSTGRES_PASSWORD
        self.dbname = settings.POSTGRES_DB
    
    def get_connection(self):
        """Create and return a PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.dbname
            )
            return conn
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {str(e)}")
    
    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """Fetch all records from a table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")
    
    def get_by_id(self, table: str, id_value: int) -> Dict[str, Any]:
        """Fetch a single record by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (id_value,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            raise Exception(f"Error fetching record: {str(e)}")
    
    def create(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a new record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = tuple(data.values())
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            return 1
        except Exception as e:
            raise Exception(f"Error creating record: {str(e)}")
    
    def update(self, table: str, id_value: int, data: Dict[str, Any]) -> int:
        """Update a record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            
            values = tuple(data.values()) + (id_value,)
            cursor.execute(query, values)
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()
            
            return rows_affected
        except Exception as e:
            raise Exception(f"Error updating record: {str(e)}")
    
    def delete(self, table: str, id_value: int) -> int:
        """Delete a record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = %s", (id_value,))
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()
            
            return rows_affected
        except Exception as e:
            raise Exception(f"Error deleting record: {str(e)}")

# Singleton instance
postgres_db = PostgresDB()
