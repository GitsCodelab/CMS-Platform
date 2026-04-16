#!/bin/bash
##############################################################################
# Script: create_connections.sh
# Purpose: Create or recreate Airflow database connections
# Connections: oracle_main, postgres_main
# Usage: ./create_connections.sh [--force]
#        --force: Delete and recreate connections even if they exist
##############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE_RECREATE="${1:-}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

##############################################################################
# Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

check_connection_exists() {
    local conn_id=$1
    if docker compose exec cms-airflow airflow connections list 2>/dev/null | grep -q "${conn_id}"; then
        return 0  # Connection exists
    else
        return 1  # Connection does not exist
    fi
}

delete_connection() {
    local conn_id=$1
    log_info "Deleting connection '${conn_id}'..."
    if docker compose exec cms-airflow airflow connections delete "${conn_id}" 2>&1 | grep -q "Successfully deleted"; then
        log_success "Connection '${conn_id}' deleted"
        return 0
    else
        log_warning "Connection '${conn_id}' does not exist (may already be deleted)"
        return 1
    fi
}

create_oracle_connection() {
    local conn_id="oracle_main"
    local host="cms-oracle-xe"
    local port="1521"
    local user="system"
    local password="oracle"
    local service="xepdb1"

    log_info "Creating Oracle connection '${conn_id}'..."
    log_info "  Host: ${host}:${port}"
    log_info "  User: ${user}"
    log_info "  Service: ${service}"

    if docker compose exec cms-airflow airflow connections add "${conn_id}" \
        --conn-type oracle \
        --conn-host "${host}" \
        --conn-port "${port}" \
        --conn-login "${user}" \
        --conn-password "${password}" \
        --conn-extra "{\"service_name\":\"${service}\"}" 2>&1 | grep -q "Successfully added"; then
        log_success "Oracle connection '${conn_id}' created successfully"
        return 0
    else
        log_error "Failed to create Oracle connection '${conn_id}'"
        return 1
    fi
}

create_postgres_connection() {
    local conn_id="postgres_main"
    local host="cms-postgresql"
    local port="5432"
    local user="postgres"
    local password="postgres"
    local database="cms"

    log_info "Creating PostgreSQL connection '${conn_id}'..."
    log_info "  Host: ${host}:${port}"
    log_info "  User: ${user}"
    log_info "  Database: ${database}"

    if docker compose exec cms-airflow airflow connections add "${conn_id}" \
        --conn-type postgres \
        --conn-host "${host}" \
        --conn-port "${port}" \
        --conn-login "${user}" \
        --conn-password "${password}" \
        --conn-schema "${database}" 2>&1 | grep -q "Successfully added"; then
        log_success "PostgreSQL connection '${conn_id}' created successfully"
        return 0
    else
        log_error "Failed to create PostgreSQL connection '${conn_id}'"
        return 1
    fi
}

verify_connections() {
    log_info "Verifying connections..."
    
    if docker compose exec cms-airflow airflow connections list 2>&1 | grep -q "oracle_main"; then
        log_success "Oracle connection 'oracle_main' verified"
    else
        log_error "Oracle connection 'oracle_main' not found!"
        return 1
    fi

    if docker compose exec cms-airflow airflow connections list 2>&1 | grep -q "postgres_main"; then
        log_success "PostgreSQL connection 'postgres_main' verified"
    else
        log_error "PostgreSQL connection 'postgres_main' not found!"
        return 1
    fi

    return 0
}

test_connections() {
    log_info "Testing connections..."
    
    if docker compose exec cms-airflow airflow connections test oracle_main 2>&1 | grep -q "Connection.*is OK"; then
        log_success "Oracle connection test passed"
    else
        log_warning "Oracle connection test may have issues (check details above)"
    fi

    if docker compose exec cms-airflow airflow connections test postgres_main 2>&1 | grep -q "Connection.*is OK"; then
        log_success "PostgreSQL connection test passed"
    else
        log_warning "PostgreSQL connection test may have issues (check details above)"
    fi
}

##############################################################################
# Main Script
##############################################################################

main() {
    echo "=========================================="
    echo "  Airflow Connection Setup Script"
    echo "=========================================="
    echo ""

    # Check if Docker is running
    if ! docker compose ps >/dev/null 2>&1; then
        log_error "Docker Compose is not running. Please start it first."
        exit 1
    fi

    log_info "Checking Airflow container status..."
    if ! docker compose exec cms-airflow airflow version >/dev/null 2>&1; then
        log_error "Airflow container is not running or not ready."
        exit 1
    fi
    log_success "Airflow is ready"
    echo ""

    # Handle force recreate flag
    if [ "${FORCE_RECREATE}" = "--force" ]; then
        log_warning "Force recreate requested. Deleting existing connections..."
        delete_connection "oracle_main" || true
        delete_connection "postgres_main" || true
        echo ""
    fi

    # Create Oracle connection if it doesn't exist
    if check_connection_exists "oracle_main"; then
        log_warning "Oracle connection 'oracle_main' already exists (use --force to recreate)"
    else
        if ! create_oracle_connection; then
            exit 1
        fi
    fi
    echo ""

    # Create PostgreSQL connection if it doesn't exist
    if check_connection_exists "postgres_main"; then
        log_warning "PostgreSQL connection 'postgres_main' already exists (use --force to recreate)"
    else
        if ! create_postgres_connection; then
            exit 1
        fi
    fi
    echo ""

    # Verify connections
    if verify_connections; then
        log_success "All connections verified successfully!"
        echo ""
        test_connections
        echo ""
        log_success "Connection setup completed successfully!"
        exit 0
    else
        log_error "Connection verification failed!"
        exit 1
    fi
}

##############################################################################
# Script Entry Point
##############################################################################

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
