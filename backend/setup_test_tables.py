#!/usr/bin/env python3
"""
Script to create test tables in Oracle and PostgreSQL databases
"""
import oracledb
import psycopg2

# Oracle Connection
try:
    print("Creating test table in Oracle...")
    oracle_conn = oracledb.connect(
        user="system",
        password="oracle",
        host="localhost",
        port=1521,
        service_name="xepdb1"
    )
    oracle_cursor = oracle_conn.cursor()
    
    # Drop table if exists
    try:
        oracle_cursor.execute("DROP TABLE test")
    except:
        pass
    
    # Create table
    oracle_cursor.execute("""
        CREATE TABLE test (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(100),
            description VARCHAR2(500),
            status VARCHAR2(50)
        )
    """)
    
    # Insert sample data
    oracle_cursor.execute("INSERT INTO test VALUES (1, 'Test Record 1', 'Sample data for testing', 'active')")
    oracle_cursor.execute("INSERT INTO test VALUES (2, 'Test Record 2', 'Another test record', 'active')")
    oracle_conn.commit()
    
    # Verify
    oracle_cursor.execute("SELECT COUNT(*) FROM test")
    count = oracle_cursor.fetchone()[0]
    print(f"✓ Oracle test table created with {count} records")
    
    oracle_cursor.close()
    oracle_conn.close()
except Exception as e:
    print(f"✗ Oracle error: {e}")

# PostgreSQL Connection
try:
    print("Creating test table in PostgreSQL...")
    pg_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="cms"
    )
    pg_cursor = pg_conn.cursor()
    
    # Drop table if exists
    try:
        pg_cursor.execute("DROP TABLE IF EXISTS test")
    except:
        pass
    
    # Create table
    pg_cursor.execute("""
        CREATE TABLE test (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            description VARCHAR(500),
            status VARCHAR(50)
        )
    """)
    
    # Insert sample data
    pg_cursor.execute("INSERT INTO test (name, description, status) VALUES (%s, %s, %s)", 
                      ('Test Record 1', 'Sample data for testing', 'active'))
    pg_cursor.execute("INSERT INTO test (name, description, status) VALUES (%s, %s, %s)", 
                      ('Test Record 2', 'Another test record', 'active'))
    pg_conn.commit()
    
    # Verify
    pg_cursor.execute("SELECT COUNT(*) FROM test")
    count = pg_cursor.fetchone()[0]
    print(f"✓ PostgreSQL test table created with {count} records")
    
    pg_cursor.close()
    pg_conn.close()
except Exception as e:
    print(f"✗ PostgreSQL error: {e}")

print("\nTest tables ready for API testing!")
