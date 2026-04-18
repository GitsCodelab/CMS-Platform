#!/bin/bash

# WSO2 Identity Server Startup Script
# Starts WSO2 IS and verifies all services are healthy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================================${NC}"
echo -e "${YELLOW}   WSO2 Identity Server Startup${NC}"
echo -e "${YELLOW}================================================${NC}"

# Check if docker compose is available
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: docker compose is not installed${NC}"
    exit 1
fi

# Check if databases are running
echo -e "\n${YELLOW}Checking PostgreSQL database...${NC}"
if docker compose ps cms-postgresql | grep -q "Up"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    docker compose up -d cms-postgresql
    sleep 10
fi

# Start WSO2 IS
echo -e "\n${YELLOW}Starting WSO2 Identity Server...${NC}"
docker compose up -d cms-wso2is

# Wait for IS to start
echo -e "\n${YELLOW}Waiting for WSO2 IS to start (this may take 1-2 minutes)...${NC}"
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -k -f https://localhost:9443/api/identity/auth/v1.0/token &>/dev/null; then
        echo -e "${GREEN}✓ WSO2 IS is healthy${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -ne "\r${YELLOW}Waiting... ($attempt/$max_attempts)${NC}"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "\n${RED}✗ WSO2 IS failed to start${NC}"
    docker compose logs cms-wso2is --tail 50
    exit 1
fi

# Verify services
echo -e "\n${YELLOW}Service Status:${NC}"
docker compose ps --format "table {{.Service}}\t{{.Status}}"

# Display access information
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}   WSO2 Identity Server is Ready!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\n${YELLOW}Access Points:${NC}"
echo -e "  Admin Console:     ${GREEN}https://localhost:9443/carbon${NC}"
echo -e "  Account Portal:    ${GREEN}https://localhost:9443/accountportal${NC}"
echo -e "  API Documentation: ${GREEN}https://localhost:9443/api-docs${NC}"
echo -e "\n${YELLOW}Credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}admin${NC}"
echo -e "\n${YELLOW}Database:${NC}"
echo -e "  Host:     ${GREEN}cms-postgresql${NC}"
echo -e "  Port:     ${GREEN}5432${NC}"
echo -e "  Database: ${GREEN}wso2is${NC}"
echo -e "  User:     ${GREEN}postgres${NC}"
echo -e "\n${YELLOW}Ports:${NC}"
echo -e "  HTTPS (9443):   Admin & API access"
echo -e "  HTTP (8280):    Gateway"
echo -e "  HTTPS (8243):   Secure Gateway"
echo -e "  HTTPS (4443):   Management"
echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  View logs:        docker compose logs cms-wso2is -f"
echo -e "  Stop service:     docker compose down"
echo -e "  Restart service:  docker compose restart cms-wso2is"
echo -e "\n${YELLOW}Note: Accept self-signed SSL certificate on first access${NC}"
echo -e "${GREEN}================================================${NC}\n"
