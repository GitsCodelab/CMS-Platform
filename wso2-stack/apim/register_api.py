#!/usr/bin/env python3
"""
WSO2 APIM - Automated API Registration Script
Registers the CMS Platform backend APIs in WSO2 API Manager
"""

import requests
import json
import sys
from datetime import datetime
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIManager:
    def __init__(self, base_url="https://localhost:9443", admin_user="admin", admin_pass="admin"):
        self.base_url = base_url
        self.admin_user = admin_user
        self.admin_pass = admin_pass
        self.access_token = None
        self.verify_ssl = False
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Get access token for API Manager"""
        try:
            self.log("Authenticating with APIM...")
            
            auth_url = f"{self.base_url}/oauth2/token"
            auth_data = {
                "grant_type": "client_credentials",
                "scope": "apim:api_create apim:api_publish"
            }
            
            response = requests.post(
                auth_url,
                auth=(self.admin_user, self.admin_pass),
                data=auth_data,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                self.log(f"✓ Authentication successful", "SUCCESS")
                return True
            else:
                self.log(f"✗ Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ Authentication error: {str(e)}", "ERROR")
            return False
            
    def get_headers(self):
        """Get headers with authorization token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def create_api(self, api_name, context, version, endpoint, sandbox_endpoint=None):
        """Create a new API"""
        try:
            self.log(f"Creating API: {api_name}...")
            
            api_url = f"{self.base_url}/api/am/publisher/v4/apis"
            
            api_data = {
                "name": api_name,
                "context": context,
                "version": version,
                "type": "HTTP",
                "endpointConfig": {
                    "endpoint_type": "http",
                    "production_endpoints": {
                        "url": endpoint
                    }
                },
                "policies": ["Unlimited"]
            }
            
            if sandbox_endpoint:
                api_data["endpointConfig"]["sandbox_endpoints"] = {
                    "url": sandbox_endpoint
                }
            
            response = requests.post(
                api_url,
                headers=self.get_headers(),
                json=api_data,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                api_id = response.json().get("id")
                self.log(f"✓ API created successfully. ID: {api_id}", "SUCCESS")
                return api_id
            else:
                self.log(f"✗ API creation failed: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"✗ API creation error: {str(e)}", "ERROR")
            return None
            
    def publish_api(self, api_id):
        """Publish an API"""
        try:
            self.log(f"Publishing API: {api_id}...")
            
            publish_url = f"{self.base_url}/api/am/publisher/v4/apis/{api_id}/publish"
            
            response = requests.post(
                publish_url,
                headers=self.get_headers(),
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.log(f"✓ API published successfully", "SUCCESS")
                return True
            else:
                self.log(f"✗ API publishing failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"✗ API publishing error: {str(e)}", "ERROR")
            return False
            
    def get_api(self, api_name):
        """Get API details by name"""
        try:
            api_url = f"{self.base_url}/api/am/publisher/v4/apis"
            
            response = requests.get(
                api_url,
                headers=self.get_headers(),
                params={"query": api_name},
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                apis = response.json().get("list", [])
                for api in apis:
                    if api.get("name") == api_name:
                        return api
            return None
                
        except Exception as e:
            self.log(f"Error getting API: {str(e)}", "ERROR")
            return None
            
    def register_apis(self):
        """Register all APIs"""
        # Authenticate first
        if not self.authenticate():
            return False
            
        self.log("=" * 70, "INFO")
        
        # Define APIs to register
        apis = [
            {
                "name": "CMS Oracle Test API",
                "context": "/cms/oracle",
                "version": "1.0.0",
                "endpoint": "http://cms-backend:8000/oracle/test",
                "sandbox": "http://cms-backend:8000/oracle/test"
            },
            {
                "name": "CMS PostgreSQL Test API",
                "context": "/cms/postgres",
                "version": "1.0.0",
                "endpoint": "http://cms-backend:8000/postgres/test",
                "sandbox": "http://cms-backend:8000/postgres/test"
            }
        ]
        
        results = []
        
        for api in apis:
            self.log(f"\nRegistering: {api['name']}", "INFO")
            self.log("-" * 70, "INFO")
            
            # Check if API already exists
            existing_api = self.get_api(api['name'])
            if existing_api:
                self.log(f"API already exists. ID: {existing_api.get('id')}", "WARN")
                results.append({
                    "name": api['name'],
                    "status": "ALREADY_EXISTS",
                    "id": existing_api.get('id')
                })
                continue
            
            # Create API
            api_id = self.create_api(
                api['name'],
                api['context'],
                api['version'],
                api['endpoint'],
                api['sandbox']
            )
            
            if api_id:
                # Publish API
                if self.publish_api(api_id):
                    results.append({
                        "name": api['name'],
                        "status": "PUBLISHED",
                        "id": api_id
                    })
                else:
                    results.append({
                        "name": api['name'],
                        "status": "CREATED_NOT_PUBLISHED",
                        "id": api_id
                    })
            else:
                results.append({
                    "name": api['name'],
                    "status": "FAILED",
                    "id": None
                })
        
        # Print summary
        self.log("=" * 70, "INFO")
        self.log("\n📊 REGISTRATION SUMMARY", "INFO")
        self.log("-" * 70, "INFO")
        
        for result in results:
            status_symbol = "✓" if result['status'] == "PUBLISHED" else "⚠" if result['status'] == "ALREADY_EXISTS" else "✗"
            self.log(f"{status_symbol} {result['name']}: {result['status']}", "INFO")
            if result['id']:
                self.log(f"   ID: {result['id']}", "INFO")
        
        self.log("\n" + "=" * 70, "INFO")
        self.log("✓ API Registration Complete!", "SUCCESS")
        self.log("\nAccess the APIs at:", "INFO")
        self.log("  Publisher: https://localhost:9443/publisher", "INFO")
        self.log("  DevPortal:  https://localhost:9443/devportal", "INFO")
        
        return True

def main():
    manager = APIManager()
    success = manager.register_apis()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
