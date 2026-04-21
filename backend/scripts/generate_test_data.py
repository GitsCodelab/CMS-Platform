#!/usr/bin/env python3
"""
Generate 100 test records for Oracle and PostgreSQL databases
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.oracle import oracle_db
from app.database.postgres import postgres_db

def generate_test_records(num_records=100):
    """Generate test records for both databases"""
    
    # Test data templates
    test_names = [
        "Product Update",
        "User Registration", 
        "Payment Processing",
        "Data Migration",
        "System Maintenance",
        "Security Patch",
        "Feature Release",
        "Bug Fix",
        "Performance Optimization",
        "Documentation Update",
    ]
    
    test_descriptions = [
        "Processing user request for system update",
        "Handling batch data import from external source",
        "Validating customer information and records",
        "Executing scheduled database maintenance task",
        "Synchronizing data across multiple systems",
        "Applying security updates to infrastructure",
        "Testing new features in staging environment",
        "Resolving critical issues in production",
        "Optimizing database query performance",
        "Updating API documentation and endpoints",
    ]
    
    statuses = ["active", "inactive"]
    
    # Generate records for Oracle
    print("🔷 Generating 100 test records for Oracle Database...")
    oracle_count = 0
    for i in range(1, num_records + 1):
        record = {
            "name": f"{test_names[(i-1) % len(test_names)]} #{i}",
            "description": f"{test_descriptions[(i-1) % len(test_descriptions)]} (Record {i})",
            "status": statuses[(i - 1) % len(statuses)]
        }
        try:
            oracle_db.create("test", record)
            oracle_count += 1
            if i % 10 == 0:
                print(f"  ✓ Created {i} Oracle records...")
        except Exception as e:
            print(f"  ✗ Error creating Oracle record {i}: {str(e)}")
    
    print(f"✅ Successfully created {oracle_count} Oracle test records\n")
    
    # Generate records for PostgreSQL
    print("🐘 Generating 100 test records for PostgreSQL Database...")
    pg_count = 0
    for i in range(1, num_records + 1):
        record = {
            "name": f"{test_names[(i-1) % len(test_names)]} #{i}",
            "description": f"{test_descriptions[(i-1) % len(test_descriptions)]} (Record {i})",
            "status": statuses[(i - 1) % len(statuses)]
        }
        try:
            postgres_db.create("test", record)
            pg_count += 1
            if i % 10 == 0:
                print(f"  ✓ Created {i} PostgreSQL records...")
        except Exception as e:
            print(f"  ✗ Error creating PostgreSQL record {i}: {str(e)}")
    
    print(f"✅ Successfully created {pg_count} PostgreSQL test records\n")
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Data Generation Complete!")
    print(f"   Oracle:     {oracle_count} records")
    print(f"   PostgreSQL: {pg_count} records")
    print(f"   Total:      {oracle_count + pg_count} records")
    print("=" * 50)

if __name__ == "__main__":
    try:
        generate_test_records(100)
        print("\n✨ All test records created successfully!")
    except Exception as e:
        print(f"\n❌ Error during test data generation: {str(e)}")
        sys.exit(1)
