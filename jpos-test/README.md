# jPOS EE Test Profile Suite

Comprehensive testing framework for jPOS Enterprise payment processing with support for multiple card brands and transaction types.

## Overview

This test suite provides:
- ✅ **Multiple Card Brands**: Visa, Mastercard, AMEX, Discover
- ✅ **Transaction Types**: Authorization, Capture, Refund, Reversal, Echo
- ✅ **Test Profiles**: Pre-configured test scenarios
- ✅ **Stress Testing**: High-volume transaction testing
- ✅ **Detailed Reporting**: Transaction status and results

## Supported Card Brands

| Brand | Test Number | Use Case |
|-------|-------------|----------|
| **Visa** | 4111111111111111 | General purpose payments |
| **Mastercard** | 5555555555554444 | Business/Corporate payments |
| **AMEX** | 378282246310005 | Premium/Travel |
| **Discover** | 6011111111111117 | Discovercard network |

## Transaction Types

| Type | Code | Description |
|------|------|-------------|
| **Authorization** | 0100 | Request authorization for transaction |
| **Capture** | 0220 | Capture previously authorized amount |
| **Refund** | 0200 | Credit transaction (refund) |
| **Reversal** | 0400 | Void/Reverse transaction |
| **Echo** | 0800 | Network connectivity test |

## Usage

### Run All Tests

```bash
python3 jposee-test-profile.py
# or
python3 jposee-test-profile.py 5
```

### Run Specific Test Suite

```bash
# Visa transactions
python3 jposee-test-profile.py 1

# Mastercard transactions
python3 jposee-test-profile.py 2

# Mixed card brands
python3 jposee-test-profile.py 3

# Stress test (10 transactions)
python3 jposee-test-profile.py 4
```

### Interactive Mode

```bash
python3 jposee-test-profile.py
# Select test when prompted
```

## Example Output

```
======================================================================
jPOS EE TEST PROFILE SUITE
======================================================================
Available Test Profiles:
1. Visa Transactions
2. Mastercard Transactions
3. Mixed Card Brands
4. Stress Test (10 transactions)
5. Run All Tests

======================================================================
VISA TRANSACTION TESTS
======================================================================

✅ Transaction: Visa Auth - $100 Purchase
   Status: PROCESSED
   Message: 0100822000000000000000000000100000000112021042014302020101114111111111111111

✅ Transaction: Visa Refund - $100 Return
   Status: PROCESSED
   Message: 0200822000000000000000000000100000000112021042014302020101114111111111111111

✅ Transaction: Visa Reversal
   Status: PROCESSED
   Message: 0400822000000000000000000000100000000112021042014302020101114111111111111111

======================================================================
TEST SUMMARY
======================================================================
Total Transactions: 4
Successful: 4 (100%)
Failed: 0 (0%)
======================================================================
```

## Transaction Amounts

Each test includes realistic transaction amounts:

- **Visa Tests**: $100, $50.99, Refund, Reversal
- **Mastercard Tests**: $250, $25, Capture, Refund
- **Mixed Tests**: $150 (AMEX), $75 (Discover), Echo tests
- **Stress Test**: Incremental amounts $10-$100

## ISO 8583 Message Format

Messages follow basic ISO 8583 structure:

```
[MTI][Processing Code][Amount][Timestamp][STAN][MCC][PAN]
```

Example:
```
0100 822000000000 000000000100 20210420143020 000001 0000 4111111111111111
```

- **0100**: Authorization request (MTI)
- **822000000000**: Processing code
- **000000000100**: Amount ($100.00)
- **20210420143020**: Transmission date/time
- **000001**: System Trace Audit Number
- **0000**: Merchant Category Code
- **4111111111111111**: Visa card number

## Test Profile Classes

### `TestTransaction`
Represents a single transaction with:
- Transaction name
- Card number
- Amount (in cents)
- Transaction type
- Description
- Timestamp

### `jPOSEETestProfile`
Manages transaction execution:
- Connects to jPOS EE on port 5001
- Sends transactions
- Captures responses
- Generates reports

## Configuration

Default settings in the test suite:

```python
host = "localhost"     # jPOS EE host
port = 5001           # jPOS EE port (jposee service)
timeout = 5           # Socket timeout (seconds)
delay = 0.5           # Delay between transactions (seconds)
```

To modify, edit the Python script or pass custom parameters.

## Creating Custom Tests

Extend the test suite by adding custom transactions:

```python
# Add to any test function
custom_test = TestTransaction(
    name="Custom Visa Test",
    card_number=CardBrand.VISA.value,
    amount=15000,  # $150.00
    trans_type=TransactionType.AUTH,
    description="Custom authorization test"
)

profile = jPOSEETestProfile(port=5001)
result = profile.send_transaction(custom_test)
profile.print_result(result)
```

## Error Handling

The test suite handles:
- **Connection Refused**: jPOS EE not running
- **Timeout**: Server not responding
- **Connection Reset**: Normal jPOS behavior (message processed)
- **Socket Errors**: Network issues

## jPOS EE Connectivity

Ensure jPOS EE is running:

```bash
# Start jPOS EE
docker compose up cms-jposee -d

# Check status
docker ps | grep cms-jposee

# View logs
docker logs cms-jposee -f
```

## Performance Notes

- **Single Transaction**: ~50-100ms
- **Batch (10 trans)**: ~1-2 seconds
- **Stress Test (10 trans)**: ~2-3 seconds

## Troubleshooting

**Connection refused error:**
```bash
# Start jPOS EE service
docker compose up cms-jposee -d
sleep 5
python3 jposee-test-profile.py
```

**Timeout errors:**
- Increase timeout in the script (edit `timeout=5` to higher value)
- Check jPOS EE logs: `docker logs cms-jposee`

**Low success rate:**
- Check jPOS EE is initialized: `docker logs cms-jposee | grep "Started"`
- Verify network connectivity: `curl http://localhost:5001`
- Check logs for processing errors

## Files in This Suite

| File | Purpose |
|------|---------|
| `jposee-test-profile.py` | Main test suite with all profiles |
| `README.md` | This documentation |
| `Python-test.py` | Basic connectivity test |
| `Python-test-improved.py` | Enhanced connectivity test |

## Next Steps

1. ✅ Run basic connectivity test: `python3 Python-test-improved.py`
2. ✅ Run visa tests: `python3 jposee-test-profile.py 1`
3. ✅ Run all tests: `python3 jposee-test-profile.py 5`
4. ✅ Analyze results and adjust configuration
5. ✅ Integrate with backend API

## Integration with CMS Backend

To integrate with the FastAPI backend:

```python
# In backend/app/routers/jpos.py
import requests

@router.post("/jpos/transaction")
def send_jpos_transaction(card_number: str, amount: int, trans_type: str):
    """Send transaction to jPOS EE"""
    # Route to jPOS EE on port 5001
    # Process response
    # Return result
```

## Support

For issues or enhancements:
1. Check jPOS logs: `docker logs cms-jposee`
2. Review test output for error details
3. Verify ISO 8583 message format
4. Check network connectivity: `nc -zv localhost 5001`
