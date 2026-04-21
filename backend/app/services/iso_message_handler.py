"""
ISO Message Handler Service
Converts raw ISO 8583 messages from jPOS into database transactions
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.database import jposee_db
from app.schemas.jposee_schemas import TransactionCreate

logger = logging.getLogger(__name__)


class ISOMessageHandler:
    """Handles ISO 8583 messages from jPOS and persists to database"""

    @staticmethod
    def handle_iso_message(iso_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse ISO 8583 message data and persist to database
        
        Args:
            iso_data: Dictionary containing ISO message fields
            
        Returns:
            Dictionary with transaction ID and status
        """
        try:
            # Map ISO fields to transaction schema
            transaction_data = ISOMessageHandler._parse_iso_fields(iso_data)
            
            # Create transaction in database (sync operation)
            result = jposee_db.create_transaction(transaction_data.__dict__)
            
            logger.info(f"✅ Transaction persisted: ID={result}, txn_id={transaction_data.txn_id}")
            
            return {
                "success": True,
                "transaction_id": result,
                "txn_id": transaction_data.txn_id,
                "message": "Transaction persisted successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to persist transaction: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to persist transaction"
            }

    @staticmethod
    def _parse_iso_fields(iso_data: Dict[str, Any]) -> TransactionCreate:
        """
        Map ISO 8583 fields to TransactionCreate schema
        
        ISO 8583 Field Mapping:
        - Field 0: Message Type Indicator (0100=Auth, 0200=Refund, etc.)
        - Field 2: Primary Account Number (PAN)
        - Field 3: Processing Code
        - Field 4: Transaction Amount
        - Field 7: Transmission Date/Time
        - Field 11: Systems Trace Audit Number (STAN)
        - Field 12: Time, Local Transaction
        - Field 13: Date, Local Transaction
        - Field 18: Merchant Category Code
        - Field 39: Response Code (00=Approved, 05=Declined, etc.)
        - Field 102: Account Identification 1
        - Field 103: Account Identification 2
        """
        
        # Extract transaction type from Message Type Indicator
        mti = iso_data.get('mti', '0100')
        txn_type = ISOMessageHandler._map_mti_to_type(mti)
        
        # Parse amount (usually stored as cents in ISO)
        amount_str = iso_data.get('field_4', '0')
        try:
            amount = float(amount_str) / 100 if amount_str else 0.0
        except (ValueError, TypeError):
            amount = 0.0
        
        # Extract PAN and get last 4 digits
        pan = iso_data.get('field_2', 'UNKNOWN')
        card_last4 = pan[-4:] if len(pan) >= 4 else pan
        
        # Extract BIN (first 6 digits)
        card_bin = pan[:6] if len(pan) >= 6 else None
        
        # Extract transaction datetime
        timestamp = iso_data.get('field_7', '')
        
        # Generate unique transaction ID if not provided
        txn_id = iso_data.get('txn_id') or iso_data.get('field_11') or f"ISO-{datetime.now().timestamp()}"
        
        # Parse response code to determine status
        response_code = iso_data.get('field_39', '00')
        status = ISOMessageHandler._map_response_code_to_status(response_code)
        
        # Build transaction object
        transaction = TransactionCreate(
            txn_id=str(txn_id),
            txn_type=txn_type,
            amount=amount,
            currency=iso_data.get('currency', 'USD'),
            card_last4=card_last4,
            card_bin=card_bin,
            merchant_id=iso_data.get('merchant_id') or iso_data.get('field_18'),
            merchant_name=iso_data.get('merchant_name'),
            status=status,
            iso_fields={
                'mti': mti,
                'processing_code': iso_data.get('field_3'),
                'stan': iso_data.get('field_11'),
                'local_txn_time': iso_data.get('field_12'),
                'local_txn_date': iso_data.get('field_13'),
                'transmission_datetime': iso_data.get('field_7'),
                'response_code': response_code,
                'account_1': iso_data.get('field_102'),
                'account_2': iso_data.get('field_103'),
            },
            routing_info={
                'source': 'jpos-iso-8583',
                'received_at': datetime.now().isoformat(),
                'raw_mti': mti,
            }
        )
        
        return transaction

    @staticmethod
    def _map_mti_to_type(mti: str) -> str:
        """Map ISO Message Type Indicator to transaction type (max 20 chars for DB)"""
        mti_map = {
            '0100': 'AUTH',
            '0110': 'AUTH_RESP',
            '0120': 'AUTH_ADVICE',
            '0200': 'REFUND',
            '0210': 'REFUND_RESP',
            '0220': 'REFUND_ADVICE',
            '0230': 'REFUND_ADV_RESP',
            '0240': 'CHARGEBACK',
            '0250': 'CHARGEBACK_RESP',
            '0260': 'CHARGEBACK_REV',
            '0300': 'FILE_UPDATE',
            '0310': 'FILE_UPDATE_RESP',
            '0400': 'REVERSAL',
            '0410': 'REVERSAL_RESP',
            '0420': 'REVERSAL_ADVICE',
            '0430': 'REVERSAL_ADV_RESP',
            '0500': 'RECONCILIATION',
            '0600': 'ADMIN',
            '0610': 'ADMIN_RESP',
            '0620': 'FILE_UPDATE_ADV',
            '0630': 'FILE_UPDATE_ADV_R',
            '0700': 'SECURE_MSG',
            '0710': 'SECURE_MSG_RESP',
            '0800': 'NETWORK_MGMT',
            '0810': 'NETWORK_MGMT_RESP',
            '0900': 'TRANSPORT',
            '0910': 'TRANSPORT_RESP',
            '0920': 'TRANSPORT_ADVICE',
            '0930': 'TRANSPORT_ADV_RESP',
        }
        return mti_map.get(mti, 'PURCHASE')

    @staticmethod
    def _map_response_code_to_status(response_code: str) -> str:
        """Map ISO response code to transaction status"""
        if response_code == '00':
            return 'approved'
        elif response_code in ['05', '51', '54', '61', '62', '68', '93', '96']:
            return 'declined'
        elif response_code in ['03', '12', '13', '14', '15', '82']:
            return 'error'
        else:
            return 'pending'

    @staticmethod
    def parse_raw_iso_string(iso_string: str) -> Dict[str, Any]:
        """
        Parse raw ISO 8583 string format into fields
        
        Simple format: MTI + fields
        Format: MTIPROCESSING_CODEAMOUNTSTANTIMESTAMP...
        
        Returns:
            Dictionary with parsed ISO fields
        """
        if len(iso_string) < 4:
            return {}
        
        parsed = {
            'mti': iso_string[0:4],  # Message Type Indicator
            'field_3': iso_string[4:10] if len(iso_string) > 4 else None,  # Processing Code
            'field_4': iso_string[10:22] if len(iso_string) > 10 else None,  # Amount
            'field_11': iso_string[22:28] if len(iso_string) > 22 else None,  # STAN
            'field_7': iso_string[28:42] if len(iso_string) > 28 else None,  # Transmission DateTime
            'field_2': iso_string[42:] if len(iso_string) > 42 else None,  # PAN (rest of string)
        }
        
        return parsed


class ISOResponseBuilder:
    """Builds ISO 8583 response messages"""
    
    @staticmethod
    def build_authorization_response(
        txn_id: str,
        approved: bool,
        amount: float,
        auth_code: str = "123456"
    ) -> str:
        """Build ISO authorization response"""
        
        mti = "0110"  # Authorization response
        response_code = "00" if approved else "05"
        
        response = (
            f"{mti}"                              # Message Type Indicator
            f"822000000000"                       # Processing code
            f"{int(amount * 100):012d}"           # Amount
            f"{datetime.now().strftime('%m%d%H%M%S')}"  # Timestamp
            f"{txn_id:6}"                         # STAN
            f"{response_code}"                    # Response code
            f"{auth_code}"                        # Authorization code
        )
        
        return response
