#!/bin/bash
set -e

echo "🚀 WSO2 APIM Automated Setup"
echo "======================================"

cd /path/to/CMS-Platform

# Step 1: Build
echo "📦 Building WSO2 APIM image..."
docker compose build --no-cache cms-apim

# Step 2: Start PostgreSQL
echo "🐳 Starting PostgreSQL..."
docker compose up cms-postgresql -d
sleep 10

# Step 3: Create database
echo "🗄️  Creating WSO2 database..."
docker exec cms-postgresql psql -U postgres -c "CREATE DATABASE wso2am;" 2>/dev/null || echo "✓ DB already exists"

# Step 4: Start APIM
echo "🚀 Starting WSO2 APIM..."
docker compose up cms-apim -d
sleep 60

# Step 5: Verify
echo ""
echo "✅ Verification:"
docker ps | grep -E "(postgresql|apim)" || echo "⚠️  Containers not found"

echo ""
echo "======================================"
echo "✅ WSO2 APIM Setup Complete!"
echo "======================================"
echo ""
echo "🔐 Access Points:"
echo "   Admin Console: https://localhost:9443/admin"
echo "   Publisher: https://localhost:9443/publisher"
echo "   Developer Portal: https://localhost:9443/devportal"
echo "   API Gateway (HTTP): http://localhost:8280"
echo "   API Gateway (HTTPS): https://localhost:8243"
echo ""
echo "🔑 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "⏱️  Note: First startup takes 2-5 minutes. Check logs: docker logs -f cms-apim"