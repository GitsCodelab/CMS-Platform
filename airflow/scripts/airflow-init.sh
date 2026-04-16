#!/bin/bash
set -euo pipefail

# Wait a bit for Postgres to be ready (pg_isready used in healthcheck)
# Run DB migrations (Airflow 3.x uses 'migrate')
airflow db migrate || true

# Remove possibly-stale connections encrypted with a different Fernet key by deleting rows
# directly from the metadata DB (avoids Airflow trying to decrypt existing passwords)
python3 - <<'PY'
import os
import psycopg2
host = os.getenv('POSTGRES_HOST', 'postgres')
db = os.getenv('POSTGRES_DB', 'airflow')
user = os.getenv('POSTGRES_USER', 'airflow')
pw = os.getenv('POSTGRES_PASSWORD', 'airflow')
try:
  conn = psycopg2.connect(host=host, dbname=db, user=user, password=pw)
  cur = conn.cursor()
  cur.execute("DELETE FROM connection WHERE conn_id IN ('bot_oracle','bot_postgres')")
  conn.commit()
  cur.close()
  conn.close()
except Exception as e:
  print('Could not delete stale connections:', e)
  pass
PY

# Recreate connections encrypted with the current Fernet key
airflow connections add bot_oracle --conn-uri "oracle+oracledb://system:oracle@cms-oracle:1521/?service_name=XE" || true
airflow connections add bot_postgres --conn-uri "postgresql://airflow:airflow@airflow-postgres:5432/airflow" || true

# Ensure SimpleAuthManager passwords file exists
if [ ! -f /opt/airflow/simple_auth_manager_passwords.json ]; then
  cat > /opt/airflow/simple_auth_manager_passwords.json <<'JSON'
{"airflow":"airflow"}
JSON
  chown 50000:0 /opt/airflow/simple_auth_manager_passwords.json || true
fi

echo "airflow-init: init complete"
