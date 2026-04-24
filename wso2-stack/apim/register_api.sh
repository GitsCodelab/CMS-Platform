#!/bin/bash

###############################################################################
# WSO2 API Manager - Automated API Registration Script
#
# Usage:
#   bash register_api.sh --name <API_NAME> --context <CONTEXT> --backend <URL>
#
# Full Options:
#   --name              (required) API display name
#   --context           (required) API context path (e.g., /api/users)
#   --backend           (required) Backend production endpoint URL
#   --version           (optional) API version (default: 1.0.0)
#   --policy            (optional) Throttle policy (default: Unlimited)
#   --sandbox-backend   (optional) Sandbox endpoint (defaults to production)
#   --host              (optional) APIM host (default: localhost)
#   --port              (optional) APIM port (default: 9443)
#   --admin             (optional) Admin username (default: admin)
#   --password          (optional) Admin password (default: admin)
#   --help              Show this help message
#
# Examples:
#   bash register_api.sh --name "User API" --context "/api/users" --backend "http://localhost:3000"
#   bash register_api.sh --name "Payment API" --context "/api/payments" \
#        --backend "https://api-prod.com" --sandbox-backend "https://api-sandbox.com" \
#        --version 2.0.0 --policy Gold
#
# Last Updated: April 24, 2026
###############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
API_VERSION="1.0.0"
THROTTLE_POLICY="Unlimited"
APIM_HOST="localhost"
APIM_PORT="9443"
ADMIN_USER="admin"
ADMIN_PASS="admin"

# Initialize variables
API_NAME=""
API_CONTEXT=""
PRODUCTION_BACKEND=""
SANDBOX_BACKEND=""

# Function: Print colored output
log() {
    local level=$1
    shift
    local message="$@"
    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
    esac
}

# Function: Print usage
usage() {
    cat << EOF
${BLUE}=== WSO2 API Manager - API Registration Script ===${NC}

${YELLOW}USAGE:${NC}
  bash register_api.sh [OPTIONS]

${YELLOW}REQUIRED OPTIONS:${NC}
  --name <API_NAME>           API display name (e.g., "User Management API")
  --context <PATH>            API context path (e.g., "/api/users")
  --backend <URL>             Backend production endpoint URL

${YELLOW}OPTIONAL OPTIONS:${NC}
  --version <VERSION>         API version (default: 1.0.0)
  --policy <POLICY>           Throttle policy (default: Unlimited)
                              Options: Unlimited, Gold, Silver, Bronze
  --sandbox-backend <URL>     Sandbox endpoint (defaults to production URL)
  --host <HOST>               APIM host (default: localhost)
  --port <PORT>               APIM port (default: 9443)
  --admin <USER>              Admin username (default: admin)
  --password <PASS>           Admin password (default: admin)
  --help                      Show this help message

${YELLOW}EXAMPLES:${NC}
  # Simple registration
  bash register_api.sh \\
    --name "User API" \\
    --context "/api/users" \\
    --backend "http://localhost:3000/users"

  # With sandbox endpoint
  bash register_api.sh \\
    --name "Payment API" \\
    --context "/api/payments" \\
    --backend "https://api-prod.example.com/payments" \\
    --sandbox-backend "https://api-sandbox.example.com/payments" \\
    --version 1.5.0 \\
    --policy Gold

  # Remote APIM instance
  bash register_api.sh \\
    --name "Remote API" \\
    --context "/api/data" \\
    --backend "http://backend.example.com" \\
    --host "apim.example.com" \\
    --port 443 \\
    --admin "apim_admin" \\
    --password "secure_pass"

EOF
}

# Function: Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                usage
                exit 0
                ;;
            --name)
                API_NAME="$2"
                shift 2
                ;;
            --context)
                API_CONTEXT="$2"
                shift 2
                ;;
            --backend)
                PRODUCTION_BACKEND="$2"
                shift 2
                ;;
            --version)
                API_VERSION="$2"
                shift 2
                ;;
            --policy)
                THROTTLE_POLICY="$2"
                shift 2
                ;;
            --sandbox-backend)
                SANDBOX_BACKEND="$2"
                shift 2
                ;;
            --host)
                APIM_HOST="$2"
                shift 2
                ;;
            --port)
                APIM_PORT="$2"
                shift 2
                ;;
            --admin)
                ADMIN_USER="$2"
                shift 2
                ;;
            --password)
                ADMIN_PASS="$2"
                shift 2
                ;;
            *)
                log ERROR "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Function: Validate required parameters
validate_inputs() {
    if [[ -z "$API_NAME" ]]; then
        log ERROR "Missing required parameter: --name"
        usage
        exit 1
    fi
    
    if [[ -z "$API_CONTEXT" ]]; then
        log ERROR "Missing required parameter: --context"
        usage
        exit 1
    fi
    
    if [[ -z "$PRODUCTION_BACKEND" ]]; then
        log ERROR "Missing required parameter: --backend"
        usage
        exit 1
    fi
    
    # If sandbox not specified, use production URL
    if [[ -z "$SANDBOX_BACKEND" ]]; then
        SANDBOX_BACKEND="$PRODUCTION_BACKEND"
    fi
}

# Function: Test APIM connectivity
test_connectivity() {
    log INFO "Testing APIM connectivity (https://${APIM_HOST}:${APIM_PORT})..."
    
    local response=$(curl -s -k -w "\n%{http_code}" \
        "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis?limit=1" \
        -u "${ADMIN_USER}:${ADMIN_PASS}" 2>/dev/null | tail -1)
    
    if [[ "$response" == "200" ]]; then
        log SUCCESS "APIM is reachable and responding"
        return 0
    else
        log ERROR "Failed to connect to APIM (HTTP $response)"
        log ERROR "Check APIM is running and credentials are correct"
        return 1
    fi
}

# Function: Register API in APIM
register_api() {
    log INFO "Registering API: $API_NAME"
    log INFO "  Context: $API_CONTEXT"
    log INFO "  Production Backend: $PRODUCTION_BACKEND"
    log INFO "  Sandbox Backend: $SANDBOX_BACKEND"
    log INFO "  Version: $API_VERSION"
    log INFO "  Policy: $THROTTLE_POLICY"
    echo ""
    
    # Construct the API registration payload
    local payload=$(cat <<EOF
{
  "name": "${API_NAME}",
  "context": "${API_CONTEXT}",
  "version": "${API_VERSION}",
  "type": "HTTP",
  "endpointConfig": {
    "endpoint_type": "http",
    "production_endpoints": {
      "url": "${PRODUCTION_BACKEND}"
    },
    "sandbox_endpoints": {
      "url": "${SANDBOX_BACKEND}"
    }
  },
  "policies": ["${THROTTLE_POLICY}"],
  "visibility": "PUBLIC"
}
EOF
)
    
    # Send registration request to APIM
    local response=$(curl -s -k -X POST \
        "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis" \
        -u "${ADMIN_USER}:${ADMIN_PASS}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    # Check if response contains an error
    if echo "$response" | grep -q '"code":400\|"code":401\|"code":500'; then
        log ERROR "Failed to register API"
        echo ""
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 1
    fi
    
    # Extract API ID from response
    local api_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    
    if [[ -z "$api_id" ]]; then
        log ERROR "Failed to extract API ID from response"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 1
    fi
    
    # Success!
    log SUCCESS "API registered successfully!"
    echo ""
    log INFO "API Details:"
    echo "  ID: $api_id"
    echo "  Name: $API_NAME"
    echo "  Context: $API_CONTEXT"
    echo "  Version: $API_VERSION"
    echo "  Status: CREATED"
    echo "  Policy: $THROTTLE_POLICY"
    echo ""
    
    # Print next steps
    log INFO "Next Steps:"
    echo "  1. Publish the API:"
    echo "     curl -X POST -k \\"
    echo "  'https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/${api_id}/state-change?action=Publish' \\"
    echo "  -u '${ADMIN_USER}:${ADMIN_PASS}'"
    echo ""
    echo "  2. View API details:"
    echo "     curl -k 'https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/${api_id}' \\"
    echo "  -u '${ADMIN_USER}:${ADMIN_PASS}' | python3 -m json.tool"
    echo ""
    echo "  3. See API_REGISTRATION_GUIDE.md for testing and subscription steps"
    echo ""
    
    return 0
}

# Function: Main execution
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  WSO2 API Manager - Automated API Registration             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate inputs
    validate_inputs
    
    # Test connectivity
    if ! test_connectivity; then
        log ERROR "Cannot proceed without APIM connectivity"
        exit 1
    fi
    echo ""
    
    # Register the API
    if register_api; then
        log SUCCESS "API registration completed successfully!"
        exit 0
    else
        log ERROR "API registration failed. Please check the error message above."
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
