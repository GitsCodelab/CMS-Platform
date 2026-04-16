#!/bin/bash
set -euo pipefail

echo "Checking for Oracle connection environment variables..."
if [ -n "${AIRFLOW_CONN_ORACLE_MAIN:-}" ]; then
  echo "Using AIRFLOW_CONN_ORACLE_MAIN to create connection 'oracle_main'"
  airflow connections add --conn-id oracle_main --conn-uri "${AIRFLOW_CONN_ORACLE_MAIN}" || true
elif [ -n "${ORACLE_HOST:-}" ]; then
  ORA_USER="${ORACLE_USER:-}" 
  ORA_PASS="${ORACLE_PASS:-}"
  ORA_HOST="${ORACLE_HOST:-}"
  ORA_PORT="${ORACLE_PORT:-1521}"
  ORA_SERVICE="${ORACLE_SERVICE:-}"
  if [ -z "$ORA_USER" ] || [ -z "$ORA_PASS" ]; then
    echo "ORACLE_USER or ORACLE_PASS not set; skipping Oracle connection creation"
    exit 0
  fi
  CONN_URI="oracle+oracledb://${ORA_USER}:${ORA_PASS}@${ORA_HOST}:${ORA_PORT}/?service_name=${ORA_SERVICE}"
  echo "Creating connection 'oracle_main' from ORACLE_* vars"
  airflow connections add --conn-id oracle_main --conn-uri "$CONN_URI" || true
else
  echo "No Oracle connection information provided; skipping"
fi
