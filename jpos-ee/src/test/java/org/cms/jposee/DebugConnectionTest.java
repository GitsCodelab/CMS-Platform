package org.cms.jposee;

import javax.persistence.*;
import org.junit.Test;

/**
 * Test to debug EntityManagerFactory creation
 */
public class DebugConnectionTest {
    
    @Test
    public void testEntityManagerFactoryCreation() {
        System.out.println("\n=== Testing EntityManagerFactory Creation ===");
        
        try {
            System.out.println("1. Calling Persistence.createEntityManagerFactory('jposee-persistence')...");
            EntityManagerFactory emf = Persistence.createEntityManagerFactory("jposee-persistence");
            System.out.println("✅ SUCCESS! EMF created: " + emf);
            emf.close();
        } catch (Exception e) {
            System.err.println("❌ FAILED: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException(e);
        }
    }
}
