package org.cms.jposee;

import javax.persistence.spi.PersistenceProvider;
import java.util.ServiceLoader;
import org.junit.Test;
import static org.junit.Assert.assertTrue;

/**
 * Debug test to check what PersistenceProviders are loaded
 */
public class PersistenceProviderTest {
    
    @Test
    public void testPersistenceProviders() {
        System.out.println("=== Checking PersistenceProviders ===");
        ServiceLoader<PersistenceProvider> loader = ServiceLoader.load(PersistenceProvider.class);
        
        int count = 0;
        for (PersistenceProvider provider : loader) {
            count++;
            System.out.println(count + ". " + provider.getClass().getName());
        }
        
        if (count == 0) {
            System.out.println("❌ NO PersistenceProviders found!");
            System.out.println("Check that META-INF/services/javax.persistence.spi.PersistenceProvider exists in JARs");
        } else {
            System.out.println("✅ Found " + count + " PersistenceProvider(s)");
        }
        
        assertTrue("At least one PersistenceProvider should be available", count > 0);
    }
}
