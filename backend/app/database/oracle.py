"""Oracle database connection and operations"""
import oracledb
from typing import List, Dict, Any
from app.config import settings


class OracleDB:
    """Oracle database operations"""

    def __init__(self):
        self.host = settings.ORACLE_HOST
        self.port = settings.ORACLE_PORT
        self.user = settings.ORACLE_USER
        self.password = settings.ORACLE_PASSWORD
        self.service = settings.ORACLE_SERVICE

    def get_connection(self):
        """Create and return an Oracle database connection"""
        try:
            conn = oracledb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                service_name=self.service
            )
            return conn
        except Exception as e:
            raise Exception(f"Oracle connection failed: {str(e)}")

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """Fetch all records from a table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")

    def get_by_id(self, table: str, id_value: int) -> Dict[str, Any]:
        """Fetch a single record by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE id = :id", {"id": id_value})
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return dict(zip(columns, row))
            return None
        except Exception as e:
            raise Exception(f"Error fetching record: {str(e)}")

    def create(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a new record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Filter out None values but keep all keys that have values
            filtered_data = {k: v for k, v in data.items() if v is not None}

            columns = ", ".join(filtered_data.keys())
            placeholders = ", ".join([f":{key}" for key in filtered_data.keys()])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            cursor.execute(query, filtered_data)
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

            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE id = :id"

            data["id"] = id_value
            cursor.execute(query, data)
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
            cursor.execute(f"DELETE FROM {table} WHERE id = :id", {"id": id_value})
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()

            return rows_affected
        except Exception as e:
            raise Exception(f"Error deleting record: {str(e)}")


# Singleton instance
oracle_db = OracleDB()
