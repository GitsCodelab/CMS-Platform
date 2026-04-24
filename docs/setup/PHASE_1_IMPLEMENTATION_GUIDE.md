# Phase 1: Foundation - Implementation Guide

**Date**: April 21, 2026  
**Status**: Ready to Execute  
**Duration**: 3-5 days  
**Objective**: Set up database schema, Hibernate configuration, and Maven dependencies  

---

## 📋 Quick Start Checklist

```
Phase 1 Deliverables:
☐ PostgreSQL schema created (iso_transactions table + audit table)
☐ Hibernate persistence.xml configured
☐ Maven dependencies added to pom.xml
☐ Database connection tested
☐ Entities created (Phase 2 prep)
```

---

## 🔧 Step 1: Create PostgreSQL Schema

### What You'll Do
Create the ISO transaction storage tables in your existing PostgreSQL database.

### Files
- **Location**: `jpos-ee/schema/01_iso_transactions_postgres.sql`
- **Status**: ✅ Created and ready to run
- **Database**: `jposee-db`

### How to Execute

#### Option A: psql Command Line
```bash
# Connect to PostgreSQL
psql -h localhost -p 5433 -U postgres -d jposee -f jpos-ee/schema/01_iso_transactions_postgres.sql

# When prompted for password, enter: postgres
```

#### Option B: DBeaver GUI (if using DBeaver)
```
1. Open DBeaver
2. Connect to jposee-db database
3. Right-click on database → New → SQL Script
4. Copy contents of 01_iso_transactions_postgres.sql
5. Execute (Ctrl+Enter)
```

#### Option C: psql Interactive
```bash
# Start psql
psql -h localhost -p 5433 -U postgres -d jposee_db

# Then copy-paste the SQL script
```

### Verification - Run These Queries

```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'iso%'
ORDER BY table_name;

-- Expected output:
-- iso_transactions
-- iso_transactions_audit

-- Verify columns in iso_transactions
\d iso_transactions

-- Verify indexes
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename = 'iso_transactions'
ORDER BY indexname;

-- Should see indexes: idx_stan, idx_rrn, idx_created_at, etc.
```

### Troubleshooting

If you get errors:

```
ERROR: permission denied
→ Make sure you're using admin user with password

ERROR: relation "iso_transactions" already exists
→ Tables already created, proceed to next step

ERROR: database "recon_dwh" does not exist
→ Check database name, use: SELECT datname FROM pg_database;
```

---

## 🔄 Step 2: Configure Hibernate

### What You'll Do
Set up Hibernate/JPA configuration to connect to PostgreSQL.

### Files
- **Location**: `jpos-ee/config/persistence.xml`
- **Status**: ✅ Created and ready to use

### How to Integrate

#### Step 2.1: Create Directory
```bash
mkdir -p jpos-ee/src/main/resources/META-INF
```

#### Step 2.2: Copy Configuration
```bash
# Copy the persistence.xml to the correct location
cp jpos-ee/config/persistence.xml jpos-ee/src/main/resources/META-INF/persistence.xml
```

#### Step 2.3: Configure Environment Variables (Optional but Recommended)

Create `jpos-ee/.env` file:
```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=jposee_db
DB_USER=postgres
DB_PASS=postgres
```

Or set in application startup:
```bash
export DB_HOST=localhost
export DB_PORT=5433
export DB_NAME=jposee
export DB_USER=postgres
export DB_PASS=postgres
```

### Configuration Details

**Current settings:**
```xml
<!-- Connection URL (localhost - for development) -->
<property name="javax.persistence.jdbc.url" 
          value="jdbc:postgresql://localhost:5433/jposee"/>

<!-- Credentials -->
<property name="javax.persistence.jdbc.user" value="postgres"/>
<property name="javax.persistence.jdbc.password" value="postgres"/>

<!-- Schema validation (don't auto-modify schema) -->
<property name="hibernate.hbm2ddl.auto" value="validate"/>

<!-- Connection pool -->
<property name="hibernate.c3p0.min_size" value="5"/>
<property name="hibernate.c3p0.max_size" value="20"/>
```

### For Docker/Production

If running in Docker, update the URL:
```xml
<!-- Docker environment (inside container) -->
<property name="javax.persistence.jdbc.url" 
          value="jdbc:postgresql://jposee-db:5433/jposee"/>
```

---

## 📦 Step 3: Add Maven Dependencies

### What You'll Do
Add required JPA/Hibernate/PostgreSQL dependencies to Maven.

### Files
- **Location**: `jpos-ee/pom_dependencies.xml`
- **Status**: ✅ Created with all dependencies listed

### How to Integrate

#### Step 3.1: Open Your pom.xml
```bash
# Location of your Maven pom.xml
vim jpos-ee/pom.xml
```

#### Step 3.2: Find Dependencies Section
```xml
<project>
    ...
    <dependencies>
        <!-- EXISTING DEPENDENCIES HERE -->
        
        <!-- ADD NEW DEPENDENCIES HERE -->
    </dependencies>
</project>
```

#### Step 3.3: Copy Dependencies
From `pom_dependencies.xml`, copy all the `<dependency>` blocks and paste into your `<dependencies>` section.

**Key dependencies to add:**
```xml
<!-- Hibernate Core -->
<dependency>
    <groupId>org.hibernate</groupId>
    <artifactId>hibernate-core</artifactId>
    <version>5.6.15.Final</version>
</dependency>

<!-- PostgreSQL Driver -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.1</version>
</dependency>

<!-- JPA API -->
<dependency>
    <groupId>javax.persistence</groupId>
    <artifactId>javax.persistence-api</artifactId>
    <version>2.2</version>
</dependency>

<!-- Logging -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>2.0.5</version>
</dependency>

<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.4.5</version>
</dependency>
```

#### Step 3.4: Download Dependencies
```bash
cd jpos-ee
mvn clean install
```

This will download ~50-100MB of dependencies. Wait for completion.

#### Step 3.5: Verify Dependencies
```bash
# Check if Hibernate is installed
mvn dependency:tree | grep hibernate

# Expected output:
# +- org.hibernate:hibernate-core:jar:5.6.15.Final:compile
# +- org.hibernate:hibernate-entitymanager:jar:5.6.15.Final:compile

# Check PostgreSQL driver
mvn dependency:tree | grep postgresql

# Expected output:
# +- org.postgresql:postgresql:jar:42.7.1:compile
```

### Troubleshooting Maven Issues

```
ERROR: Plugin 'org.apache.maven.plugins:maven-compiler-plugin' not found
→ Run: mvn help:describe -Dplugin=org.apache.maven.plugins:maven-compiler-plugin

ERROR: Missing POM parent
→ Check parent pom.xml reference

ERROR: Duplicate dependencies
→ Run: mvn dependency:analyze
→ Remove duplicates

ERROR: Version conflicts
→ Run: mvn dependency:tree -Dverbose
→ Look for [OMITTED] entries
```

---

## 🧪 Step 4: Test Database Connection

### What You'll Do
Verify that Hibernate can connect to PostgreSQL.

### Create Test Class
**File**: `jpos-ee/src/test/java/org/cms/jposee/ConnectionTest.java`

```java
package org.cms.jposee;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;
import org.junit.Test;
import static org.junit.Assert.assertNotNull;

public class ConnectionTest {
    
    @Test
    public void testDatabaseConnection() {
        // Create EntityManagerFactory from persistence.xml
        EntityManagerFactory emf = Persistence.createEntityManagerFactory("jposee-persistence");
        assertNotNull("EntityManagerFactory should not be null", emf);
        
        // Create EntityManager
        EntityManager em = emf.createEntityManager();
        assertNotNull("EntityManager should not be null", em);
        
        // Test connection
        try {
            em.getTransaction().begin();
            // Simple query to test connection
            em.createNativeQuery("SELECT 1").getResultList();
            em.getTransaction().commit();
            System.out.println("✅ Database connection successful!");
        } finally {
            em.close();
            emf.close();
        }
    }
}
```

### Run Test
```bash
cd jpos-ee
mvn test -Dtest=ConnectionTest
```

### Expected Output
```
✅ Database connection successful!
BUILD SUCCESS
```

### If Test Fails

**Error**: Connection refused
```
ERROR: Connection refused
→ Check PostgreSQL is running: sudo systemctl status postgresql
→ Check port: netstat -an | grep 5433
→ Check credentials in persistence.xml
```

**Error**: Invalid database name
```
ERROR: database "recon_dwh" does not exist
→ Verify database exists: psql -U postgres -l
→ Check persistence.xml URL
```

**Error**: Hibernate not found
```
ERROR: Hibernate classes not found
→ Run: mvn clean compile
→ Check Maven dependencies: mvn dependency:tree
```

---

## ✅ Phase 1 Completion Checklist

Before moving to Phase 2, verify:

- [ ] PostgreSQL schema created
  ```sql
  SELECT COUNT(*) FROM information_schema.tables 
  WHERE table_name = 'iso_transactions';
  -- Should return: 1
  ```

- [ ] Hibernate persistence.xml in place
  ```bash
  ls -la jpos-ee/src/main/resources/META-INF/persistence.xml
  # Should exist
  ```

- [ ] Maven dependencies downloaded
  ```bash
  mvn dependency:tree | grep -c "org.hibernate"
  # Should return > 0
  ```

- [ ] Database connection working
  ```bash
  mvn test -Dtest=ConnectionTest
  # Should show BUILD SUCCESS
  ```

---

## 📝 What Comes Next (Phase 2)

Once Phase 1 is complete, you'll move to Phase 2:

**Phase 2 Tasks:**
1. Create JPA Entity classes (IsoTransaction.java, IsoTransactionAudit.java)
2. Create Repository classes for database access
3. Write entity mapping tests
4. Verify schema matches entities

**Estimated Time**: 5-7 days

---

## 🚨 Important Notes

### Database Backup
Before running schema script, backup your database:
```bash
pg_dump -U postgres jposee > backup_jposee_$(date +%Y%m%d).sql
```

### Reverting Changes
If something goes wrong:
```sql
-- Drop tables (WARNING: This deletes data!)
DROP TABLE iso_transactions_audit CASCADE;
DROP TABLE iso_transactions CASCADE;

-- Then re-run schema script
```

### Production Considerations
- [ ] Change default passwords
- [ ] Use environment variables for credentials
- [ ] Set `hibernate.hbm2ddl.auto` to `validate`
- [ ] Enable SSL for database connection
- [ ] Set up database backups
- [ ] Configure connection pool for high volume

---

## 📞 Getting Help

If you encounter issues:

1. **Check logs**: Look for detailed error messages
2. **Verify configuration**: Double-check persistence.xml values
3. **Test connectivity**: Use psql directly to verify connection
4. **Check permissions**: Ensure admin user has privileges
5. **Run diagnostics**: `mvn dependency:analyze`

---

## ⏱️ Timeline

**Typical timeline for Phase 1:**

- Day 1: Create schema + verify (1-2 hours)
- Day 2: Add Maven dependencies + build (1-2 hours)
- Day 3: Configure Hibernate + test connection (1-2 hours)
- Days 4-5: Troubleshooting + verification (as needed)

**Total**: 3-5 business days

---

## 📌 Summary

**Phase 1 is now ready to execute!**

You have:
✅ Database schema ready to deploy  
✅ Hibernate configuration ready  
✅ Maven dependencies documented  
✅ Test procedure documented  

**Next Action**: Run Step 1 (Create PostgreSQL Schema)

When you're done with Phase 1, we'll move to **Phase 2: Create JPA Entities**
