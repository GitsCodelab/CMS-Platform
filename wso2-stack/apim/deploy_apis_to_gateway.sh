#!/bin/bash

###############################################################################
# Deploy APIs to WSO2 APIM Gateway
#
# This script publishes and deploys APIs to the gateway
#
# Usage: bash deploy_apis_to_gateway.sh
#
# Last Updated: April 24, 2026
###############################################################################

set -e

APIM_HOST="${APIM_HOST:-localhost}"
APIM_PORT="${APIM_PORT:-9443}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-admin}"
GATEWAY_ENVIRONMENT="${GATEWAY_ENVIRONMENT:-Default}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  WSO2 APIM - Deploy APIs to Gateway                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# API IDs to deploy
API_IDS=(
    "554f2aa3-96c3-4564-afde-df183f22344b"  # CMS Oracle Test API
    "9b2aecdf-bc33-4d47-ba43-79894b50d4f1"  # CMS PostgreSQL Test API  
    "e3624596-e686-4235-a33f-e80a27692038"  # Order Management API
)

echo -e "${YELLOW}Step 1: Check API Status${NC}"
echo "Fetching all APIs..."
curl -s -k "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis" \
  -u "${ADMIN_USER}:${ADMIN_PASS}" | python3 << 'PYEOF'
import json, sys
data = json.load(sys.stdin)
for api in data.get('list', []):
    print(f"  - {api['name']:30} | Status: {api['lifeCycleStatus']:12} | Context: {api['context']}")
PYEOF

echo ""
echo -e "${YELLOW}Step 2: Deploy each API${NC}"

for API_ID in "${API_IDS[@]}"; do
    echo ""
    echo "Processing API: $API_ID"
    
    # Get API details
    API_DATA=$(curl -s -k "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/$API_ID" \
        -u "${ADMIN_USER}:${ADMIN_PASS}")
    
    API_NAME=$(echo "$API_DATA" | python3 -c "import json, sys; print(json.load(sys.stdin).get('name', 'Unknown'))" 2>/dev/null || echo "Unknown")
    
    echo "  API Name: $API_NAME"
    
    # Try to create a revision and deploy it
    # First, let's try to update the API to trigger revision creation
    REVISION_RESPONSE=$(curl -s -k -X PUT \
        "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/$API_ID" \
        -u "${ADMIN_USER}:${ADMIN_PASS}" \
        -H "Content-Type: application/json" \
        -d "$API_DATA" 2>&1)
    
    if echo "$REVISION_RESPONSE" | grep -q '"id"'; then
        echo -e "  ${GREEN}✓ API revision created${NC}"
        
        # Now deploy to gateway
        # Try to deploy to the Default gateway
        DEPLOY_RESPONSE=$(curl -s -k -X POST \
            "https://${APIM_HOST}:${APIM_PORT}/api/am/publisher/v4/apis/$API_ID/revisions/0/deploy-by-label" \
            -u "${ADMIN_USER}:${ADMIN_PASS}" \
            -H "Content-Type: application/json" \
            -d '{"vhost":"localhost"}' 2>&1)
        
        if echo "$DEPLOY_RESPONSE" | grep -q '"id"\|"status"'; then
            echo -e "  ${GREEN}✓ API deployed to gateway${NC}"
        else
            echo -e "  ${YELLOW}⚠ Deploy response: ${DEPLOY_RESPONSE:0:100}${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ Could not update API${NC}"
    fi
done

echo ""
echo -e "${YELLOW}Step 3: Verify Gateway Deployment${NC}"
echo "Testing gateway endpoints..."
echo ""

declare -A API_CONTEXTS
API_CONTEXTS["554f2aa3-96c3-4564-afde-df183f22344b"]="/cms/oracle"
API_CONTEXTS["9b2aecdf-bc33-4d47-ba43-79894b50d4f1"]="/cms/postgres"
API_CONTEXTS["e3624596-e686-4235-a33f-e80a27692038"]="/api/orders"

for API_ID in "${!API_CONTEXTS[@]}"; do
    CONTEXT="${API_CONTEXTS[$API_ID]}"
    
    # Try to hit the API through the gateway
    RESPONSE=$(curl -s -w "\n%{http_code}" -i "http://localhost:8280${CONTEXT}/" 2>&1)
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "  ${GREEN}✓ ${CONTEXT:1} - HTTP $HTTP_CODE${NC}"
    elif [ "$HTTP_CODE" = "404" ]; then
        echo -e "  ${RED}✗ ${CONTEXT:1} - HTTP $HTTP_CODE (Not Deployed)${NC}"
    else
        echo -e "  ${YELLOW}⚠ ${CONTEXT:1} - HTTP $HTTP_CODE${NC}"
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Access APIM Publisher: https://${APIM_HOST}:${APIM_PORT}/publisher"
echo "  2. For each API, click 'Publish' to make it available"
echo "  3. Go to API > Deployments to verify gateway deployment"
echo "  4. Test APIs at:"
echo "     - http://localhost:8280/cms/oracle/"
echo "     - http://localhost:8280/cms/postgres/"
echo "     - http://localhost:8280/api/orders/"
echo ""
echo "Note: APIs must be Published and Deployed to be accessible through gateway"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
