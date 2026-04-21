package org.cms.jposee;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.assertNotNull;

/**
 * Test database connection with Hibernate/PostgreSQL
 * Verifies that:
 * 1. Hibernate can connect to PostgreSQL
 * 2. persistence.xml is properly configured
 * 3. EntityManager factory initializes without errors
 */
public class ConnectionTest {
    
    private EntityManagerFactory emf;
    private EntityManager em;
    
    @Before
    public void setUp() {
        System.out.println("=".repeat(70));
        System.out.println("Testing Hibernate/PostgreSQL Connection");
        System.out.println("=".repeat(70));
        System.out.println("Initializing EntityManagerFactory...");
        
        try {
            emf = Persistence.createEntityManagerFactory("jposee-persistence");
            assertNotNull("EntityManagerFactory should not be null", emf);
            System.out.println("✅ EntityManagerFactory created successfully");
        } catch (Exception e) {
            System.err.println("❌ Failed to create EntityManagerFactory: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }
    
    @Test
    public void testDatabaseConnection() {
        System.out.println("\nCreating EntityManager...");
        
        try {
            em = emf.createEntityManager();
            assertNotNull("EntityManager should not be null", em);
            System.out.println("✅ EntityManager created successfully");
            
            // Test connection by executing a simple native query
            System.out.println("\nExecuting test query...");
            Object resultObj = em.createNativeQuery("SELECT COUNT(*) FROM iso_transactions")
                    .getSingleResult();
            Long result = ((Number) resultObj).longValue();
            
            System.out.println("✅ Database query executed successfully");
            System.out.println("   iso_transactions table exists with " + result + " records");
            
            // Verify audit table
            System.out.println("\nVerifying iso_transactions_audit table...");
            Object auditObj = em.createNativeQuery("SELECT COUNT(*) FROM iso_transactions_audit")
                    .getSingleResult();
            Long auditCount = ((Number) auditObj).longValue();
            System.out.println("✅ iso_transactions_audit table exists with " + auditCount + " records");
            
            System.out.println("\n" + "=".repeat(70));
            System.out.println("✅ DATABASE CONNECTION TEST SUCCESSFUL!");
            System.out.println("=".repeat(70));
            System.out.println("Summary:");
            System.out.println("  - Hibernate: ✅ Working");
            System.out.println("  - PostgreSQL: ✅ Connected");
            System.out.println("  - Database: jposee");
            System.out.println("  - Tables: iso_transactions, iso_transactions_audit");
            System.out.println("=".repeat(70));
            
        } catch (Exception e) {
            System.err.println("\n❌ Database connection test failed:");
            System.err.println("   Error: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }
    
    @After
    public void tearDown() {
        if (em != null && em.isOpen()) {
            em.close();
        }
        if (emf != null && emf.isOpen()) {
            emf.close();
        }
        System.out.println("\nResources cleaned up.");
    }
}
