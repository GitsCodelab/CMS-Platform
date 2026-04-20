#!/usr/bin/env python3
"""
Script to create and initialize test tables in Oracle and PostgreSQL databases
Supports both Docker container names and localhost connections
"""
import oracledb
import psycopg2
import sys
from datetime import datetime


def log(message, level="INFO"):
    """Print timestamped log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def init_oracle(host="cms-oracle-xe", port=1521, user="system", password="oracle", service="xepdb1"):
    """Initialize test table in Oracle database"""
    try:
        log("Connecting to Oracle database...")
        conn = oracledb.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            service_name=service
        )
        cursor = conn.cursor()
        
        # Drop table if exists
        try:
            cursor.execute("DROP TABLE test")
            log("Dropped existing test table from Oracle")
        except Exception as e:
            log(f"No existing table to drop (expected): {str(e)[:50]}", "DEBUG")
            pass
        
        # Create table
        cursor.execute("""
            CREATE TABLE test (
                id NUMBER PRIMARY KEY,
                name VARCHAR2(100),
                description VARCHAR2(500),
                status VARCHAR2(50)
            )
        """)
        log("✓ Test table created in Oracle")
        
        # Insert sample data
        test_data = [
            (1, 'Test Record 1', 'Sample data for testing', 'active'),
            (2, 'Test Record 2', 'Another test record', 'active'),
            (3, 'Test Record 3', 'Third test record', 'inactive'),
            (4, 'Test Record 4', 'Fourth record for verification', 'active'),
            (5, 'Test Record 5', 'Final test record', 'inactive'),
        ]
        
        for record in test_data:
            cursor.execute(
                "INSERT INTO test (id, name, description, status) VALUES (:1, :2, :3, :4)",
                record
            )
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM test")
        count = cursor.fetchone()[0]
        log(f"✓ Oracle: {count} test records created successfully", "SUCCESS")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log(f"✗ Oracle initialization failed: {str(e)}", "ERROR")
        return False


def init_postgres(host="cms-postgresql", port=5432, user="postgres", password="postgres", database="cms"):
    """Initialize test table in PostgreSQL database"""
    try:
        log("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Drop table if exists
        try:
            cursor.execute("DROP TABLE IF EXISTS test CASCADE")
            log("Dropped existing test table from PostgreSQL")
        except Exception as e:
            log(f"No existing table to drop (expected): {str(e)[:50]}", "DEBUG")
        
        # Create table
        cursor.execute("""
            CREATE TABLE test (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                description VARCHAR(500),
                status VARCHAR(50)
            )
        """)
        log("✓ Test table created in PostgreSQL")
        
        # Insert sample data
        test_data = [
            ('Test Record 1', 'Sample data for testing', 'active'),
            ('Test Record 2', 'Another test record', 'active'),
            ('Test Record 3', 'Third test record', 'inactive'),
            ('Test Record 4', 'Fourth record for verification', 'active'),
            ('Test Record 5', 'Final test record', 'inactive'),
        ]
        
        for name, description, status in test_data:
            cursor.execute(
                "INSERT INTO test (name, description, status) VALUES (%s, %s, %s)",
                (name, description, status)
            )
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM test")
        count = cursor.fetchone()[0]
        log(f"✓ PostgreSQL: {count} test records created successfully", "SUCCESS")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log(f"✗ PostgreSQL initialization failed: {str(e)}", "ERROR")
        return False


def main():
    """Initialize both databases"""
    log("Starting test table initialization...", "INFO")
    print("-" * 60)
    
    # Parse command line arguments for custom host/port
    oracle_host = "cms-oracle-xe"
    postgres_host = "cms-postgresql"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "localhost":
            oracle_host = "localhost"
            postgres_host = "localhost"
            log("Using localhost connections", "INFO")
        elif sys.argv[1] in ["--help", "-h"]:
            print("Usage: python3 init_test_tables.py [localhost]")
            print("  - No args: Use Docker container names (default)")
            print("  - localhost: Use localhost connections")
            return 0
    
    print()
    oracle_ok = init_oracle(host=oracle_host)
    print()
    postgres_ok = init_postgres(host=postgres_host)
    print()
    print("-" * 60)
    
    if oracle_ok and postgres_ok:
        log("✓ Both databases initialized successfully!", "SUCCESS")
        return 0
    else:
        log("✗ One or more databases failed to initialize", "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
