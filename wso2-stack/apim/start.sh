#!/bin/bash

# WSO2 API Manager Quick Start Script
# This script initializes and starts WSO2 APIM with all necessary configurations

set -e

echo "=========================================="
echo "WSO2 API Manager - Quick Start"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check if Docker Compose is available
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed.${NC}"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version --short)
echo -e "${GREEN}✓ Docker Compose v${COMPOSE_VERSION} is available${NC}"
echo ""

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../" && pwd )"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Starting WSO2 APIM and dependencies...${NC}"
echo ""

# Start PostgreSQL first (required for APIM)
echo -e "${YELLOW}Starting PostgreSQL database...${NC}"
docker compose up -d cms-postgresql

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
until docker exec cms-postgresql pg_isready -U postgres &> /dev/null; do
    echo "Waiting..."
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Start WSO2 APIM
echo -e "${YELLOW}Starting WSO2 API Manager...${NC}"
docker compose up -d cms-apim

# Wait for APIM to start (this can take 2-3 minutes)
echo -e "${YELLOW}Waiting for WSO2 APIM to initialize (this may take 2-3 minutes)...${NC}"
for i in {1..120}; do
    if docker exec cms-apim curl -s -k https://localhost:9443/api/am/admin/v0.17/system-info &> /dev/null; then
        echo -e "${GREEN}✓ WSO2 APIM is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Verify all services are running
echo -e "${YELLOW}Verifying services...${NC}"
echo ""

SERVICES=("cms-postgresql" "cms-apim")
ALL_RUNNING=true

for service in "${SERVICES[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" --quiet | grep -q .; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is NOT running${NC}"
        ALL_RUNNING=false
    fi
done

echo ""

if [ "$ALL_RUNNING" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "✓ WSO2 APIM Started Successfully!"
    echo "==========================================${NC}"
    echo ""
    echo "Access WSO2 APIM:"
    echo "  Admin Console: https://localhost:9443/admin"
    echo "  Publisher Portal: https://localhost:9443/publisher"
    echo "  Developer Portal: https://localhost:9443/devportal"
    echo ""
    echo "Credentials:"
    echo "  Username: admin"
    echo "  Password: admin"
    echo ""
    echo "API Gateway Endpoints:"
    echo "  HTTP: http://localhost:8280"
    echo "  HTTPS: https://localhost:8243"
    echo ""
    echo "Note: Use 'https://localhost:8243/cms/v1' as your API base URL"
    echo ""
    echo "Logs:"
    echo "  WSO2 APIM: docker logs -f cms-apim"
    echo "  PostgreSQL: docker logs -f cms-postgresql"
    echo ""
else
    echo -e "${RED}Some services failed to start. Check logs with: docker logs cms-apim${NC}"
    exit 1
fi
