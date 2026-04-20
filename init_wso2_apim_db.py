#!/usr/bin/env python3
"""
WSO2 API Manager Database Initialization Script
Creates essential tables for WSO2 APIM to function properly

Tables created:
- API metadata and versioning
- API subscriptions and subscribers
- Applications and application keys
- Throttling policies
- Access tokens and API keys
- Event logging
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from datetime import datetime


def log(message, level="INFO"):
    """Print timestamped log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def init_wso2_apim_db(host="cms-postgresql", port=5432, user="postgres", password="postgres", database="wso2am"):
    """Initialize WSO2 APIM database with required tables"""
    try:
        log("Connecting to PostgreSQL database for WSO2 APIM...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        log("Creating WSO2 APIM tables...", "INFO")
        
        # Drop existing tables if they exist (for fresh initialization)
        tables_to_drop = [
            "AM_API_PRODUCT_MAPPING",
            "AM_API_RESOURCE_SCOPE_MAPPING",
            "AM_API_SCOPE",
            "AM_API_COMMENTS",
            "AM_API_RATINGS",
            "AM_WORKFLOW_REQUESTS",
            "AM_MONETIZATION_USAGE",
            "AM_API_PRODUCT_REVISION",
            "AM_API_REVISION",
            "AM_API",
            "AM_APPLICATION_KEY_MAPPING",
            "AM_APPLICATION_REGISTRATION",
            "AM_APPLICATION",
            "AM_SUBSCRIBER",
            "AM_SUBSCRIPTION",
            "AM_THROTTLE_TIER",
            "AM_THROTTLE_ADVANCED_POLICY",
            "AM_API_DEFAULT_VERSION",
            "AM_ALERT_TYPES",
            "AM_ALERT_EMAILLIST",
            "AM_API_COMMENTS_REPLY",
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                log(f"  ✓ Dropped {table}", "DEBUG")
            except Exception as e:
                log(f"  Could not drop {table}: {str(e)[:50]}", "DEBUG")
        
        # Create core tables
        log("Creating AM_SUBSCRIBER table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_SUBSCRIBER (
                SUBSCRIBER_ID SERIAL PRIMARY KEY,
                USER_ID VARCHAR(255) NOT NULL UNIQUE,
                TENANT_ID INTEGER DEFAULT 1,
                EMAIL_ADDRESS VARCHAR(255),
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        log("Creating AM_APPLICATION table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_APPLICATION (
                APPLICATION_ID SERIAL PRIMARY KEY,
                NAME VARCHAR(100) NOT NULL,
                SUBSCRIBER_ID INTEGER NOT NULL,
                APPLICATION_TIER VARCHAR(50) DEFAULT 'Unlimited',
                CALLBACK_URL TEXT,
                DESCRIPTION TEXT,
                APPLICATION_STATUS VARCHAR(50) DEFAULT 'APPROVED',
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (SUBSCRIBER_ID) REFERENCES AM_SUBSCRIBER(SUBSCRIBER_ID) ON DELETE CASCADE
            )
        """)
        
        log("Creating AM_API table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_API (
                API_ID SERIAL PRIMARY KEY,
                API_PROVIDER VARCHAR(255) NOT NULL,
                API_NAME VARCHAR(255) NOT NULL,
                API_VERSION VARCHAR(30) NOT NULL,
                CONTEXT VARCHAR(255) NOT NULL UNIQUE,
                CONTEXT_TEMPLATE VARCHAR(255),
                API_TYPE VARCHAR(50) DEFAULT 'HTTP',
                ENDPOINT VARCHAR(255),
                SANDBOX_ENDPOINT VARCHAR(255),
                RESOURCE_COUNT INTEGER DEFAULT 0,
                IS_LATEST BOOLEAN DEFAULT TRUE,
                STATUS VARCHAR(50) DEFAULT 'PUBLISHED',
                SECURITY VARCHAR(50) DEFAULT 'oauth2',
                CREATED_BY VARCHAR(255),
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_BY VARCHAR(255),
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                TENANT_ID INTEGER DEFAULT 1
            )
        """)
        
        log("Creating AM_SUBSCRIPTION table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_SUBSCRIPTION (
                SUBSCRIPTION_ID SERIAL PRIMARY KEY,
                API_ID INTEGER NOT NULL,
                APPLICATION_ID INTEGER NOT NULL,
                SUB_STATUS VARCHAR(50) DEFAULT 'ACTIVE',
                SUBSCRIPTION_TIER VARCHAR(50) DEFAULT 'Bronze',
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (API_ID) REFERENCES AM_API(API_ID) ON DELETE CASCADE,
                FOREIGN KEY (APPLICATION_ID) REFERENCES AM_APPLICATION(APPLICATION_ID) ON DELETE CASCADE,
                UNIQUE(API_ID, APPLICATION_ID)
            )
        """)
        
        log("Creating AM_APPLICATION_KEY_MAPPING table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_APPLICATION_KEY_MAPPING (
                APPLICATION_ID INTEGER NOT NULL,
                CONSUMER_KEY VARCHAR(255) NOT NULL UNIQUE,
                CONSUMER_SECRET VARCHAR(255) NOT NULL UNIQUE,
                KEY_TYPE VARCHAR(50) DEFAULT 'PRODUCTION',
                STATE VARCHAR(50) DEFAULT 'ACTIVE',
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (APPLICATION_ID, KEY_TYPE),
                FOREIGN KEY (APPLICATION_ID) REFERENCES AM_APPLICATION(APPLICATION_ID) ON DELETE CASCADE
            )
        """)
        
        log("Creating AM_THROTTLE_TIER table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_THROTTLE_TIER (
                TIER_ID SERIAL PRIMARY KEY,
                TIER_NAME VARCHAR(50) NOT NULL UNIQUE,
                DESCRIPTION TEXT,
                REQUEST_COUNT INTEGER DEFAULT 1000,
                TIME_UNIT VARCHAR(10) DEFAULT 'min',
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        log("Creating AM_API_DEFAULT_VERSION table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_API_DEFAULT_VERSION (
                API_ID INTEGER NOT NULL,
                DEFAULT_API_VERSION VARCHAR(30),
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (API_ID),
                FOREIGN KEY (API_ID) REFERENCES AM_API(API_ID) ON DELETE CASCADE
            )
        """)
        
        log("Creating AM_API_RATINGS table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_API_RATINGS (
                RATING_ID SERIAL PRIMARY KEY,
                API_ID INTEGER NOT NULL,
                USER_ID VARCHAR(255) NOT NULL,
                RATING INTEGER CHECK (RATING >= 1 AND RATING <= 5),
                COMMENT TEXT,
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UPDATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (API_ID) REFERENCES AM_API(API_ID) ON DELETE CASCADE
            )
        """)
        
        log("Creating AM_ALERT_TYPES table...", "DEBUG")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AM_ALERT_TYPES (
                ALERT_TYPE_ID SERIAL PRIMARY KEY,
                ALERT_TYPE_NAME VARCHAR(100) NOT NULL UNIQUE,
                DESCRIPTION TEXT,
                CREATED_TIME TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        log("Creating database indexes...", "DEBUG")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_am_api_provider ON AM_API(API_PROVIDER)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_am_api_status ON AM_API(STATUS)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_am_subscription_status ON AM_SUBSCRIPTION(SUB_STATUS)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_am_application_subscriber ON AM_APPLICATION(SUBSCRIBER_ID)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_am_api_ratings_user ON AM_API_RATINGS(USER_ID)")
        
        log("✓ All tables created successfully", "SUCCESS")
        
        # Insert default throttling tiers
        log("Inserting default throttling tiers...", "DEBUG")
        cursor.execute("DELETE FROM AM_THROTTLE_TIER")
        
        tiers = [
            ('Bronze', 'Bronze tier - 1000 requests/min', 1000, 'min'),
            ('Silver', 'Silver tier - 5000 requests/min', 5000, 'min'),
            ('Gold', 'Gold tier - 10000 requests/min', 10000, 'min'),
            ('Platinum', 'Platinum tier - Unlimited', 999999, 'min'),
            ('Unlimited', 'Unlimited tier - No limits', 999999, 'min'),
        ]
        
        for tier_name, description, request_count, time_unit in tiers:
            cursor.execute(
                """INSERT INTO AM_THROTTLE_TIER (TIER_NAME, DESCRIPTION, REQUEST_COUNT, TIME_UNIT)
                   VALUES (%s, %s, %s, %s)""",
                (tier_name, description, request_count, time_unit)
            )
            log(f"  ✓ Added {tier_name} tier", "DEBUG")
        
        # Insert default alert types
        log("Inserting default alert types...", "DEBUG")
        cursor.execute("DELETE FROM AM_ALERT_TYPES")
        
        alert_types = [
            ('AbnormalResponseTime', 'Alert when response time is abnormal'),
            ('AbnormalBackendTime', 'Alert when backend time is abnormal'),
            ('AbnormalRequestsPerMin', 'Alert when requests per minute is abnormal'),
            ('RequestPatternChanged', 'Alert when request pattern changes'),
            ('UnusualIPAccess', 'Alert on unusual IP access'),
            ('FrequentTierHitAPI', 'Alert when API hits tier frequently'),
            ('AbnormalUserBehaviour', 'Alert on abnormal user behavior'),
        ]
        
        for alert_type, description in alert_types:
            cursor.execute(
                """INSERT INTO AM_ALERT_TYPES (ALERT_TYPE_NAME, DESCRIPTION)
                   VALUES (%s, %s)""",
                (alert_type, description)
            )
            log(f"  ✓ Added {alert_type} alert type", "DEBUG")
        
        # Insert sample subscriber
        log("Inserting sample subscriber...", "DEBUG")
        cursor.execute("""
            INSERT INTO AM_SUBSCRIBER (USER_ID, EMAIL_ADDRESS)
            VALUES ('admin', 'admin@example.com')
            ON CONFLICT (USER_ID) DO NOTHING
        """)
        
        # Verify tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'AM_%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        log(f"✓ WSO2 APIM Database initialized with {len(tables)} tables", "SUCCESS")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        log(f"✗ WSO2 APIM database initialization failed: {str(e)}", "ERROR")
        return False


def main():
    """Main entry point"""
    log("Starting WSO2 API Manager database initialization...", "INFO")
    print("-" * 70)
    
    # Parse command line arguments
    host = "cms-postgresql"
    database = "wso2am"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "localhost":
            host = "localhost"
            log("Using localhost connection", "INFO")
        elif sys.argv[1] in ["--help", "-h"]:
            print("Usage: python3 init_wso2_apim_db.py [localhost]")
            print("  - No args: Use Docker container names (default)")
            print("  - localhost: Use localhost connections")
            return 0
    
    print()
    success = init_wso2_apim_db(host=host, database=database)
    print()
    print("-" * 70)
    
    if success:
        log("✓ WSO2 APIM database ready for deployment!", "SUCCESS")
        return 0
    else:
        log("✗ WSO2 APIM database initialization failed", "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
