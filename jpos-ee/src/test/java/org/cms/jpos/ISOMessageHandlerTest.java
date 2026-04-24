package org.cms.jpos;

import org.junit.Before;
import org.junit.Test;
import org.cms.jpos.ISOMessageHandler.SimpleISOMessage;

import static org.junit.Assert.*;

/**
 * Test suite for ISO 8583 Message Handler
 * Covers different business case scenarios
 */
public class ISOMessageHandlerTest {

    @Before
    public void setUp() {
        ISOMessageHandler.clearTransactionLog();
    }

    /**
     * Test 1: Authorization Request with Valid Payment
     * Tests standard payment authorization flow
     */
    @Test
    public void testAuthorizationRequest_ValidPayment() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0100");
        request.set(2, "4532123456789012");  // PAN
        request.set(4, "000000010000");      // Amount $100.00
        request.set(11, "123456");           // STAN
        request.set(12, "121500");           // Time
        request.set(13, "0424");             // Date

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0110", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
        assertEquals("123456", response.get(38)); // Auth code
    }

    /**
     * Test 2: Balance Inquiry
     * Tests balance check operation
     */
    @Test
    public void testBalanceInquiry_CheckBalance() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0200");
        request.set(2, "4532123456789012");  // PAN
        request.set(11, "123457");           // STAN
        request.set(12, "121500");           // Time
        request.set(13, "0424");             // Date

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0210", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
        assertEquals("840000000000001000", response.get(54)); // Balance
    }

    /**
     * Test 3: Financial Transaction - Successful Withdrawal
     * Tests ATM withdrawal scenario
     */
    @Test
    public void testFinancialTransaction_SuccessfulWithdrawal() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0220");
        request.set(2, "4532123456789012");  // PAN
        request.set(4, "000000005000");      // Amount $50.00
        request.set(11, "123458");           // STAN
        request.set(12, "121500");           // Time
        request.set(13, "0424");             // Date

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0230", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
        assertEquals("123456", response.get(38)); // Auth code
    }

    /**
     * Test 4: Transaction Reversal
     * Tests failed transaction reversal
     */
    @Test
    public void testTransactionReversal_ReverseFailedTransaction() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0400");
        request.set(2, "4532123456789012");  // PAN
        request.set(4, "000000020000");      // Amount $200.00
        request.set(37, "000001234567");     // RRN

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0410", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
    }

    /**
     * Test 5: PIN Change
     * Tests PIN update operation
     */
    @Test
    public void testPINChange_UpdatePIN() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0600");
        request.set(2, "4532123456789012");  // PAN
        request.set(11, "123459");           // STAN
        request.set(12, "121500");           // Time

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0610", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
    }

    /**
     * Test 6: Echo Test
     * Tests network connectivity check
     */
    @Test
    public void testEchoTest_ConnectivityCheck() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0800");
        request.set(11, "123460");           // STAN
        request.set(12, "121500");           // Time

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0810", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
    }

    /**
     * Test 7: Logoff
     * Tests session termination
     */
    @Test
    public void testLogoff_CloseSession() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("0500");
        request.set(11, "123461");           // STAN
        request.set(12, "121500");           // Time

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("0510", response.getMTI());
        assertEquals("00", response.get(39));  // Approved
    }

    /**
     * Test 8: Invalid Message Type
     * Tests error handling for unknown message type
     */
    @Test
    public void testInvalidMessageType_ErrorHandling() {
        SimpleISOMessage request = new SimpleISOMessage();
        request.setMTI("9999");  // Invalid message type

        SimpleISOMessage response = ISOMessageHandler.processMessage(request);

        assertNotNull(response);
        assertEquals("30", response.get(39));  // Format error
    }

    /**
     * Test 9: Multiple Transactions - Stress Test
     * Tests multiple concurrent-like message handling
     */
    @Test
    public void testMultipleTransactions_StressTest() {
        for (int i = 0; i < 10; i++) {
            SimpleISOMessage request = new SimpleISOMessage();
            request.setMTI("0100");
            request.set(2, "4532123456789012");
            request.set(4, "000000010000");
            request.set(11, String.format("%06d", 123400 + i));
            request.set(12, "121500");
            request.set(13, "0424");

            SimpleISOMessage response = ISOMessageHandler.processMessage(request);

            assertNotNull(response);
            assertEquals("0110", response.getMTI());
            assertEquals("00", response.get(39));
        }
    }

    /**
     * Test 10: Generic Handler - Multiple Message Types
     * Tests main message router with different message types
     */
    @Test
    public void testProcessMessage_GenericHandler() {
        // Test authorization
        SimpleISOMessage authRequest = new SimpleISOMessage();
        authRequest.setMTI("0100");
        authRequest.set(2, "4532123456789012");
        authRequest.set(4, "000000010000");

        SimpleISOMessage authResponse = ISOMessageHandler.processMessage(authRequest);
        assertEquals("0110", authResponse.getMTI());
        assertEquals("00", authResponse.get(39));

        // Test balance inquiry
        SimpleISOMessage balanceRequest = new SimpleISOMessage();
        balanceRequest.setMTI("0200");
        balanceRequest.set(2, "4532123456789012");

        SimpleISOMessage balanceResponse = ISOMessageHandler.processMessage(balanceRequest);
        assertEquals("0210", balanceResponse.getMTI());
        assertEquals("00", balanceResponse.get(39));
    }
}
