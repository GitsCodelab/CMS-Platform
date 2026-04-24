#!/usr/bin/env python3
"""
Register all APIs in WSO2 APIM 4.3.0 with proper CORS and Gateway Configuration
Configuration: Default Gateway from deployment.toml with full CORS enabled

Usage:
    python3 register_apis.py

Author: CMS Platform Team
Date: April 24, 2026
"""
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

APIM_HOST = "localhost"
APIM_PORT = "9443"
USERNAME = "admin"
PASSWORD = "admin"
API_URL = f"https://{APIM_HOST}:{APIM_PORT}/api/am/publisher/v4"

# API Configurations
APIS_CONFIG = [
    {
        "name": "CMS Oracle Test API",
        "context": "/cms/oracle",
        "version": "1.0.0",
        "endpoint": "http://cms-backend:8000/oracle/test",
        "description": "Oracle Database API for CMS Platform"
    },
    {
        "name": "CMS PostgreSQL Test API",
        "context": "/cms/postgres",
        "version": "1.0.0",
        "endpoint": "http://cms-backend:8000/postgres/test",
        "description": "PostgreSQL Database API for CMS Platform"
    },
    {
        "name": "Order Management API",
        "context": "/api/orders",
        "version": "1.5.0",
        "endpoint": "http://cms-backend:8000/orders/test",
        "description": "Order Management API for CMS Platform"
    }
]

CORS_CONFIG = {
    "corsConfigurationEnabled": True,
    "accessControlAllowCredentials": True,
    "accessControlAllowOrigins": ["*"],
    "accessControlAllowHeaders": [
        "authorization",
        "Access-Control-Allow-Origin",
        "Content-Type",
        "SOAPAction",
        "X-API-Key"
    ],
    "accessControlAllowMethods": [
        "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
    ]
}

print("📋 WSO2 APIM API REGISTRATION")
print("=" * 80)
print(f"Target: {APIM_HOST}:{APIM_PORT}")
print(f"Gateway: Default (from deployment.toml)")
print(f"CORS: Enabled for all origins\n")

# Fetch existing APIs
print("🔍 Fetching existing APIs...")
existing_resp = requests.get(
    f"{API_URL}/apis",
    auth=(USERNAME, PASSWORD),
    verify=False
)

existing_apis = {api['name']: api['id'] for api in existing_resp.json().get('list', [])}
print(f"   Found {len(existing_apis)} existing APIs\n")

# Register/Update APIs
registered_apis = []

for api_config in APIS_CONFIG:
    api_name = api_config['name']
    print(f"📝 Processing: {api_name}")
    
    if api_name in existing_apis:
        # Update existing API
        api_id = existing_apis[api_name]
        print(f"   ✓ Updating existing API (ID: {api_id})")
        
        # Fetch current config
        api_response = requests.get(
            f"{API_URL}/apis/{api_id}",
            auth=(USERNAME, PASSWORD),
            verify=False
        )
        
        if api_response.status_code == 200:
            api_data = api_response.json()
            
            # Update endpoint
            if 'endpoint' in api_data and isinstance(api_data['endpoint'], list):
                for ep in api_data['endpoint']:
                    if 'inline' in ep:
                        ep['inline']['list'][0]['url'] = api_config['endpoint']
            
            # Update CORS
            api_data['corsConfiguration'] = CORS_CONFIG.copy()
            
            # Update API
            update_resp = requests.put(
                f"{API_URL}/apis/{api_id}",
                auth=(USERNAME, PASSWORD),
                json=api_data,
                verify=False
            )
            
            if update_resp.status_code in [200, 201]:
                print(f"   ✅ Updated successfully")
                registered_apis.append({'name': api_name, 'id': api_id, 'status': 'UPDATED'})
            else:
                print(f"   ⚠️  Update failed: {update_resp.status_code}")
    else:
        # Register new API
        print(f"   ✓ Registering new API")
        
        api_payload = {
            "name": api_name,
            "context": api_config['context'],
            "version": api_config['version'],
            "provider": "admin",
            "type": "REST",
            "description": api_config['description'],
            "endpoint": [
                {
                    "type": "http",
                    "inline": {
                        "endpointType": "HTTP",
                        "list": [
                            {
                                "name": "default",
                                "url": api_config['endpoint']
                            }
                        ]
                    }
                }
            ],
            "corsConfiguration": CORS_CONFIG.copy()
        }
        
        create_resp = requests.post(
            f"{API_URL}/apis",
            auth=(USERNAME, PASSWORD),
            json=api_payload,
            verify=False
        )
        
        if create_resp.status_code in [200, 201]:
            new_api = create_resp.json()
            new_api_id = new_api.get('id', 'unknown')
            print(f"   ✅ Registered successfully (ID: {new_api_id})")
            registered_apis.append({'name': api_name, 'id': new_api_id, 'status': 'CREATED'})
        else:
            print(f"   ❌ Failed: {create_resp.status_code}")

print("\n" + "=" * 80)
print(f"\n✅ API REGISTRATION COMPLETE")
print(f"   Total: {len(registered_apis)} APIs processed")

for api in registered_apis:
    status_icon = "🔄" if api['status'] == 'UPDATED' else "✨"
    print(f"   {status_icon} {api['name']} ({api['status']})")

print("\n" + "=" * 80)
print("\n📊 Configuration Summary:")
print("   Gateway: Default (deployment.toml)")
print("   CORS Enabled: Yes")
print("   Allow Origins: *")
print("   Allow Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS")

print("\n✨ Next Steps:")
print("   1. Access DevPortal: https://localhost:9443/devportal")
print("   2. Subscribe to APIs")
print("   3. Test via API Console")
