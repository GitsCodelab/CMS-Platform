"""jPOS EE database operations for PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.config import settings


class JposEEDB:
    """jPOS EE database operations for PostgreSQL"""

    def __init__(self):
        self.host = settings.POSTGRES_HOST
        self.port = settings.POSTGRES_PORT
        self.user = settings.POSTGRES_USER
        self.password = settings.POSTGRES_PASSWORD
        self.dbname = settings.POSTGRES_DB

    def get_connection(self):
        """Create and return a PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.dbname
            )
            return conn
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {str(e)}")

    # ========================================================================
    # TRANSACTION OPERATIONS
    # ========================================================================

    def create_transaction(self, data: Dict[str, Any]) -> int:
        """Create a new transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO jposee_transactions 
                (txn_id, txn_type, amount, currency, status, card_last4, card_bin, 
                 merchant_id, merchant_name, merchant_category, iso_fields, 
                 routing_info, gateway_response, duration_ms, retry_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            values = (
                data.get('txn_id'),
                data.get('txn_type'),
                data.get('amount'),
                data.get('currency', 'USD'),
                data.get('status'),
                data.get('card_last4'),
                data.get('card_bin'),
                data.get('merchant_id'),
                data.get('merchant_name'),
                data.get('merchant_category'),
                json.dumps(data.get('iso_fields')) if data.get('iso_fields') else None,
                json.dumps(data.get('routing_info')) if data.get('routing_info') else None,
                json.dumps(data.get('gateway_response')) if data.get('gateway_response') else None,
                data.get('duration_ms'),
                data.get('retry_count', 0)
            )

            cursor.execute(query, values)
            txn_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return txn_id
        except Exception as e:
            raise Exception(f"Error creating transaction: {str(e)}")

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by database ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM jposee_transactions WHERE id = %s
            """

            cursor.execute(query, (transaction_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return self._format_transaction(dict(row))
            return None
        except Exception as e:
            raise Exception(f"Error fetching transaction: {str(e)}")

    def get_transaction_by_txn_id(self, txn_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by transaction ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM jposee_transactions WHERE txn_id = %s
            """

            cursor.execute(query, (txn_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return self._format_transaction(dict(row))
            return None
        except Exception as e:
            raise Exception(f"Error fetching transaction: {str(e)}")

    def list_transactions(self, filters: Dict[str, Any] = None) -> Tuple[List[Dict], int]:
        """List transactions with filtering and pagination"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            filters = filters or {}
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            offset = (page - 1) * limit

            # Build WHERE clause
            where_clauses = []
            params = []

            if filters.get('status'):
                where_clauses.append("status = %s")
                params.append(filters['status'])

            if filters.get('txn_type'):
                where_clauses.append("txn_type = %s")
                params.append(filters['txn_type'])

            if filters.get('merchant_id'):
                where_clauses.append("merchant_id = %s")
                params.append(filters['merchant_id'])

            if filters.get('card_bin'):
                where_clauses.append("card_bin = %s")
                params.append(filters['card_bin'])

            if filters.get('date_from'):
                where_clauses.append("timestamp >= %s")
                params.append(filters['date_from'])

            if filters.get('date_to'):
                where_clauses.append("timestamp <= %s")
                params.append(filters['date_to'])

            if filters.get('amount_min'):
                where_clauses.append("amount >= %s")
                params.append(filters['amount_min'])

            if filters.get('amount_max'):
                where_clauses.append("amount <= %s")
                params.append(filters['amount_max'])

            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_clauses.append("(txn_id ILIKE %s OR merchant_name ILIKE %s OR card_last4 LIKE %s)")
                params.extend([search_term, search_term, filters['search']])

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Get total count
            count_query = f"SELECT COUNT(*) as cnt FROM jposee_transactions WHERE {where_clause}"
            cursor.execute(count_query, params)
            count_result = cursor.fetchone()
            total = count_result['cnt'] if count_result else 0

            # Get paginated results
            query = f"""
                SELECT * FROM jposee_transactions 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            transactions = [self._format_transaction(dict(row)) for row in rows]
            return transactions, total
        except Exception as e:
            raise Exception(f"Error listing transactions: {str(e)}")

    def update_transaction(self, transaction_id: int, data: Dict[str, Any]) -> int:
        """Update a transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            update_fields = []
            values = []

            if 'status' in data:
                update_fields.append("status = %s")
                values.append(data['status'])

            if 'gateway_response' in data:
                update_fields.append("gateway_response = %s")
                values.append(json.dumps(data['gateway_response']) if data['gateway_response'] else None)

            if 'duration_ms' in data:
                update_fields.append("duration_ms = %s")
                values.append(data['duration_ms'])

            if 'retry_count' in data:
                update_fields.append("retry_count = %s")
                values.append(data['retry_count'])

            update_fields.append("updated_at = CURRENT_TIMESTAMP")

            query = f"""
                UPDATE jposee_transactions 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            values.append(transaction_id)

            cursor.execute(query, values)
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()

            return rows_affected
        except Exception as e:
            raise Exception(f"Error updating transaction: {str(e)}")

    def _format_transaction(self, row: Dict) -> Dict:
        """Format transaction row from database"""
        # RealDictCursor already deserializes JSONB to dict, but handle both cases
        if row.get('iso_fields'):
            if isinstance(row['iso_fields'], str):
                row['iso_fields'] = json.loads(row['iso_fields'])
        if row.get('routing_info'):
            if isinstance(row['routing_info'], str):
                row['routing_info'] = json.loads(row['routing_info'])
        if row.get('gateway_response'):
            if isinstance(row['gateway_response'], str):
                row['gateway_response'] = json.loads(row['gateway_response'])
        return row

    # ========================================================================
    # ROUTING RULE OPERATIONS
    # ========================================================================

    def create_routing_rule(self, data: Dict[str, Any]) -> int:
        """Create a new routing rule"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO jposee_routing_rules 
                (rule_name, rule_description, enabled, priority, criteria, action, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            values = (
                data.get('rule_name'),
                data.get('rule_description'),
                data.get('enabled', True),
                data.get('priority', 0),
                json.dumps(data.get('criteria', {})),
                json.dumps(data.get('action', {})),
                data.get('created_by')
            )

            cursor.execute(query, values)
            rule_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return rule_id
        except Exception as e:
            raise Exception(f"Error creating routing rule: {str(e)}")

    def get_routing_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """Get routing rule by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM jposee_routing_rules WHERE id = %s"
            cursor.execute(query, (rule_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return self._format_routing_rule(dict(row))
            return None
        except Exception as e:
            raise Exception(f"Error fetching routing rule: {str(e)}")

    def list_routing_rules(self, filters: Dict[str, Any] = None) -> Tuple[List[Dict], int]:
        """List routing rules with pagination"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            filters = filters or {}
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            offset = (page - 1) * limit

            # Count total
            count_query = "SELECT COUNT(*) as cnt FROM jposee_routing_rules WHERE enabled = %s"
            cursor.execute(count_query, (filters.get('enabled', True),))
            count_result = cursor.fetchone()
            total = count_result['cnt'] if count_result else 0

            # Get paginated results
            query = """
                SELECT * FROM jposee_routing_rules 
                WHERE enabled = %s
                ORDER BY priority DESC, created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (filters.get('enabled', True), limit, offset))
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            rules = [self._format_routing_rule(dict(row)) for row in rows]
            return rules, total
        except Exception as e:
            raise Exception(f"Error listing routing rules: {str(e)}")

    def update_routing_rule(self, rule_id: int, data: Dict[str, Any]) -> int:
        """Update a routing rule"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            update_fields = []
            values = []

            if 'rule_name' in data:
                update_fields.append("rule_name = %s")
                values.append(data['rule_name'])

            if 'rule_description' in data:
                update_fields.append("rule_description = %s")
                values.append(data['rule_description'])

            if 'enabled' in data:
                update_fields.append("enabled = %s")
                values.append(data['enabled'])

            if 'priority' in data:
                update_fields.append("priority = %s")
                values.append(data['priority'])

            if 'criteria' in data:
                update_fields.append("criteria = %s")
                values.append(json.dumps(data['criteria']))

            if 'action' in data:
                update_fields.append("action = %s")
                values.append(json.dumps(data['action']))

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                if 'updated_by' in data:
                    update_fields.append("updated_by = %s")
                    values.append(data['updated_by'])

                query = f"""
                    UPDATE jposee_routing_rules 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                values.append(rule_id)

                cursor.execute(query, values)
                conn.commit()
                rows_affected = cursor.rowcount

            else:
                rows_affected = 0

            cursor.close()
            conn.close()

            return rows_affected
        except Exception as e:
            raise Exception(f"Error updating routing rule: {str(e)}")

    def delete_routing_rule(self, rule_id: int) -> int:
        """Delete a routing rule"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "DELETE FROM jposee_routing_rules WHERE id = %s"
            cursor.execute(query, (rule_id,))
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()

            return rows_affected
        except Exception as e:
            raise Exception(f"Error deleting routing rule: {str(e)}")

    def _format_routing_rule(self, row: Dict) -> Dict:
        """Format routing rule row from database"""
        # RealDictCursor already deserializes JSONB to dict
        if row.get('criteria'):
            if isinstance(row['criteria'], str):
                row['criteria'] = json.loads(row['criteria'])
        if row.get('action'):
            if isinstance(row['action'], str):
                row['action'] = json.loads(row['action'])
        return row

    # ========================================================================
    # AUDIT LOG OPERATIONS
    # ========================================================================

    def create_audit_log(self, data: Dict[str, Any]) -> int:
        """Create an audit log entry"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO jposee_audit_logs 
                (action_type, user_id, username, ip_address, user_agent, resource_type, 
                 resource_id, result, error_message, details, changes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            values = (
                data.get('action_type'),
                data.get('user_id'),
                data.get('username'),
                data.get('ip_address'),
                data.get('user_agent'),
                data.get('resource_type'),
                data.get('resource_id'),
                data.get('result'),
                data.get('error_message'),
                json.dumps(data.get('details')) if data.get('details') else None,
                json.dumps(data.get('changes')) if data.get('changes') else None
            )

            cursor.execute(query, values)
            audit_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return audit_id
        except Exception as e:
            raise Exception(f"Error creating audit log: {str(e)}")

    def list_audit_logs(self, filters: Dict[str, Any] = None) -> Tuple[List[Dict], int]:
        """List audit logs with filtering and pagination"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            filters = filters or {}
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            offset = (page - 1) * limit

            # Build WHERE clause
            where_clauses = []
            params = []

            if filters.get('action_type'):
                where_clauses.append("action_type = %s")
                params.append(filters['action_type'])

            if filters.get('user_id'):
                where_clauses.append("user_id = %s")
                params.append(filters['user_id'])

            if filters.get('resource_type'):
                where_clauses.append("resource_type = %s")
                params.append(filters['resource_type'])

            if filters.get('result'):
                where_clauses.append("result = %s")
                params.append(filters['result'])

            if filters.get('date_from'):
                where_clauses.append("timestamp >= %s")
                params.append(filters['date_from'])

            if filters.get('date_to'):
                where_clauses.append("timestamp <= %s")
                params.append(filters['date_to'])

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Get total count
            count_query = f"SELECT COUNT(*) as cnt FROM jposee_audit_logs WHERE {where_clause}"
            cursor.execute(count_query, params)
            count_result = cursor.fetchone()
            total = count_result['cnt'] if count_result else 0

            # Get paginated results
            query = f"""
                SELECT * FROM jposee_audit_logs 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            audit_logs = [self._format_audit_log(dict(row)) for row in rows]
            return audit_logs, total
        except Exception as e:
            raise Exception(f"Error listing audit logs: {str(e)}")

    def _format_audit_log(self, row: Dict) -> Dict:
        """Format audit log row from database"""
        # RealDictCursor already deserializes JSONB to dict
        if row.get('details'):
            if isinstance(row['details'], str):
                row['details'] = json.loads(row['details'])
        if row.get('changes'):
            if isinstance(row['changes'], str):
                row['changes'] = json.loads(row['changes'])
        return row

    # ========================================================================
    # BATCH JOB OPERATIONS
    # ========================================================================

    def create_batch_job(self, data: Dict[str, Any]) -> int:
        """Create a new batch job"""
        try:
            import uuid
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO jposee_batch_jobs 
                (batch_id, batch_name, status, total_records, file_path, file_type, 
                 mapping, rules, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            values = (
                data.get('batch_id') or f"BATCH-{uuid.uuid4().hex[:12].upper()}",
                data.get('batch_name'),
                data.get('status', 'pending'),
                data.get('total_records'),
                data.get('file_path'),
                data.get('file_type'),
                json.dumps(data.get('mapping', {})),
                json.dumps(data.get('rules')) if data.get('rules') else None,
                data.get('created_by')
            )

            cursor.execute(query, values)
            job_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return job_id
        except Exception as e:
            raise Exception(f"Error creating batch job: {str(e)}")

    def get_batch_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get batch job by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM jposee_batch_jobs WHERE id = %s"
            cursor.execute(query, (job_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return self._format_batch_job(dict(row))
            return None
        except Exception as e:
            raise Exception(f"Error fetching batch job: {str(e)}")

    def list_batch_jobs(self, filters: Dict[str, Any] = None) -> Tuple[List[Dict], int]:
        """List batch jobs with pagination"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            filters = filters or {}
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            offset = (page - 1) * limit

            # Build WHERE clause
            where_clauses = []
            params = []

            if filters.get('status'):
                where_clauses.append("status = %s")
                params.append(filters['status'])

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Get total count
            count_query = f"SELECT COUNT(*) as cnt FROM jposee_batch_jobs WHERE {where_clause}"
            cursor.execute(count_query, params)
            count_result = cursor.fetchone()
            total = count_result['cnt'] if count_result else 0

            # Get paginated results
            query = f"""
                SELECT * FROM jposee_batch_jobs 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(query, params)
            rows = cursor.fetchall()

            cursor.close()
            conn.close()

            jobs = [self._format_batch_job(dict(row)) for row in rows]
            return jobs, total
        except Exception as e:
            raise Exception(f"Error listing batch jobs: {str(e)}")

    def update_batch_job(self, job_id: int, data: Dict[str, Any]) -> int:
        """Update a batch job"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            update_fields = []
            values = []

            if 'status' in data:
                update_fields.append("status = %s")
                values.append(data['status'])

            if 'processed_records' in data:
                update_fields.append("processed_records = %s")
                values.append(data['processed_records'])

            if 'successful_records' in data:
                update_fields.append("successful_records = %s")
                values.append(data['successful_records'])

            if 'failed_records' in data:
                update_fields.append("failed_records = %s")
                values.append(data['failed_records'])

            if 'started_at' in data:
                update_fields.append("started_at = %s")
                values.append(data['started_at'])

            if 'completed_at' in data:
                update_fields.append("completed_at = %s")
                values.append(data['completed_at'])

            if 'duration_ms' in data:
                update_fields.append("duration_ms = %s")
                values.append(data['duration_ms'])

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")

                query = f"""
                    UPDATE jposee_batch_jobs 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                values.append(job_id)

                cursor.execute(query, values)
                conn.commit()
                rows_affected = cursor.rowcount
            else:
                rows_affected = 0

            cursor.close()
            conn.close()

            return rows_affected
        except Exception as e:
            raise Exception(f"Error updating batch job: {str(e)}")

    def _format_batch_job(self, row: Dict) -> Dict:
        """Format batch job row from database"""
        # RealDictCursor already deserializes JSONB to dict
        if row.get('mapping'):
            if isinstance(row['mapping'], str):
                row['mapping'] = json.loads(row['mapping'])
        if row.get('rules'):
            if isinstance(row['rules'], str):
                row['rules'] = json.loads(row['rules'])
        return row

    # ========================================================================
    # MONITORING & METRICS
    # ========================================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get today's stats
            query = """
                SELECT
                    COUNT(*) as total_transactions,
                    COUNT(*) FILTER (WHERE status = 'success') as successful_transactions,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_transactions,
                    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / NULLIF(COUNT(*), 0), 2) as success_rate_percent,
                    ROUND(AVG(duration_ms), 2) as avg_response_time_ms,
                    MAX(timestamp) as last_transaction_timestamp
                FROM jposee_transactions
                WHERE DATE(timestamp) = CURRENT_DATE
            """

            cursor.execute(query)
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            return dict(result) if result else {}
        except Exception as e:
            raise Exception(f"Error fetching dashboard stats: {str(e)}")

    def get_routing_analytics(self) -> List[Dict[str, Any]]:
        """Get routing rules analytics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    id,
                    rule_name,
                    hit_count,
                    success_count,
                    failed_count,
                    ROUND(CAST(100.0 * success_count / NULLIF(hit_count, 0) AS NUMERIC), 2) as success_rate_percent,
                    ROUND(CAST(CAST(total_duration_ms AS FLOAT) / NULLIF(hit_count, 0) AS NUMERIC), 2) as avg_processing_ms
                FROM jposee_routing_rules
                WHERE enabled = TRUE
                ORDER BY hit_count DESC
            """

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return [dict(row) for row in results]
        except Exception as e:
            raise Exception(f"Error fetching routing analytics: {str(e)}")
