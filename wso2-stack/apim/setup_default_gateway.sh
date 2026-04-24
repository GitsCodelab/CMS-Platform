#!/bin/bash

###############################################################################
# WSO2 APIM - Default Gateway Configuration
#
# This script creates a default gateway profile in WSO2 APIM
# with standard production-ready settings.
#
# Usage:
#   bash setup_default_gateway.sh
#
# Last Updated: April 24, 2026
###############################################################################

set -e

# Configuration
APIM_HOST="${APIM_HOST:-localhost}"
APIM_PORT="${APIM_PORT:-9443}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-admin}"
GATEWAY_NAME="${GATEWAY_NAME:-Default Gateway}"
GATEWAY_ID="${GATEWAY_ID:-default}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  WSO2 APIM - Default Gateway Setup                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Configuration:${NC}"
echo "  APIM Host: $APIM_HOST"
echo "  APIM Port: $APIM_PORT"
echo "  Gateway Name: $GATEWAY_NAME"
echo "  Gateway ID: $GATEWAY_ID"
echo ""

# Test connectivity
echo -e "${YELLOW}Testing APIM connectivity...${NC}"
if ! curl -s -k "https://${APIM_HOST}:${APIM_PORT}/api/am/admin/v3/gateways" \
    -u "${ADMIN_USER}:${ADMIN_PASS}" > /dev/null 2>&1; then
    echo -e "${RED}✗ Cannot connect to APIM at https://${APIM_HOST}:${APIM_PORT}${NC}"
    echo "  Please ensure APIM is running and credentials are correct"
    exit 1
fi
echo -e "${GREEN}✓ APIM is reachable${NC}"
echo ""

# Create gateway payload
GATEWAY_PAYLOAD=$(cat <<'EOF'
{
  "name": "Default Gateway",
  "displayName": "Default Gateway",
  "description": "Default production gateway for API traffic",
  "gatewayType": "Regular",
  "supportedApiTypes": ["HTTP", "SOAP", "GraphQL", "WebSocket"],
  "endpoint": {
    "host": "localhost",
    "port": 8280,
    "https": {
      "enabled": true,
      "port": 8243
    },
    "webSocket": {
      "enabled": true,
      "port": 9099
    }
  },
  "properties": {
    "Organization": "carbon.super",
    "ApiVersion": "v4",
    "Environment": "production",
    "LoadBalance": {
      "Algorithm": "round_robin",
      "SessionAffinity": false
    },
    "TLS": {
      "MinVersion": "TLSv1.2",
      "MaxVersion": "TLSv1.3",
      "CipherSuites": [
        "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
      ]
    },
    "RateLimiting": {
      "Enabled": true,
      "GlobalThrottleLimit": 10000,
      "PerSecondLimit": 100
    },
    "Security": {
      "EnableSSL": true,
      "EnableClientAuthentication": false,
      "AllowedCiphers": "all"
    },
    "ApiGateway": {
      "Environment": "Production",
      "VHost": "localhost",
      "WebAppContext": "/",
      "CORSEnabled": true,
      "CORSAllowOrigins": "*",
      "CORSAllowMethods": "GET,POST,PUT,DELETE,PATCH,OPTIONS",
      "CORSAllowHeaders": "authorization,Access-Control-Allow-Origin,Content-Type,SOAPAction"
    }
  }
}
EOF
)

# Create gateway via REST API
echo -e "${YELLOW}Creating default gateway...${NC}"

RESPONSE=$(curl -s -k -X POST \
    "https://${APIM_HOST}:${APIM_PORT}/api/am/admin/v3/gateways" \
    -u "${ADMIN_USER}:${ADMIN_PASS}" \
    -H "Content-Type: application/json" \
    -d "$GATEWAY_PAYLOAD")

# Check response
if echo "$RESPONSE" | grep -q '"id"'; then
    GATEWAY_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 'unknown'))" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ Gateway created successfully${NC}"
    echo "  Gateway ID: $GATEWAY_ID"
    echo ""
elif echo "$RESPONSE" | grep -q '"already exist"'; then
    echo -e "${YELLOW}⚠ Default gateway already exists${NC}"
    echo "  Skipping creation..."
    echo ""
else
    echo -e "${RED}✗ Failed to create gateway${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

# Verify gateway
echo -e "${YELLOW}Verifying gateway configuration...${NC}"
VERIFY=$(curl -s -k \
    "https://${APIM_HOST}:${APIM_PORT}/api/am/admin/v3/gateways" \
    -u "${ADMIN_USER}:${ADMIN_PASS}")

GATEWAY_COUNT=$(echo "$VERIFY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('list', [])))" 2>/dev/null || echo "0")

if [ "$GATEWAY_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Gateway verified - Total gateways: $GATEWAY_COUNT${NC}"
    echo ""
    echo -e "${GREEN}✓ Default gateway setup complete!${NC}"
    echo ""
    echo "Gateway Details:"
    echo "  Name: Default Gateway"
    echo "  Type: Regular (HTTP/SOAP/GraphQL/WebSocket)"
    echo "  HTTP Port: 8280"
    echo "  HTTPS Port: 8243"
    echo "  WebSocket Port: 9099"
    echo ""
    echo "Next Steps:"
    echo "  1. Access APIM Publisher: https://${APIM_HOST}:${APIM_PORT}/publisher"
    echo "  2. Register your APIs"
    echo "  3. Publish APIs to this gateway"
    echo "  4. APIs will be available at:"
    echo "     - HTTP:  http://${APIM_HOST}:8280/api-context"
    echo "     - HTTPS: https://${APIM_HOST}:8243/api-context"
    echo ""
else
    echo -e "${RED}✗ Verification failed${NC}"
    exit 1
fi
