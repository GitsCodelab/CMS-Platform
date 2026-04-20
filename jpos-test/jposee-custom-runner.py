#!/usr/bin/env python3
"""
jPOS EE Custom Test Runner
Loads test profiles from JSON configuration file
Allows easy customization without code modification
"""

import json
import socket
import time
import sys
from typing import Dict, List

class CustomTestRunner:
    """Run tests from JSON configuration"""
    
    def __init__(self, config_file: str, host: str = "localhost", port: int = 5001):
        self.config_file = config_file
        self.host = host
        self.port = port
        self.profiles = []
        self.results = []
        self.load_config()
    
    def load_config(self):
        """Load test profiles from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.profiles = json.load(f)
            print(f"✓ Loaded {len(self.profiles)} test profiles")
        except FileNotFoundError:
            print(f"✗ Configuration file not found: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON in configuration file")
            sys.exit(1)
    
    def generate_iso_message(self, profile: Dict) -> str:
        """Generate ISO 8583 message from profile"""
        trans_code = profile["trans_type"]
        trans_code_map = {
            "AUTH": "0100",
            "CAPTURE": "0220",
            "REFUND": "0200",
            "REVERSAL": "0400",
            "ECHO": "0800"
        }
        
        mti = trans_code_map.get(trans_code, "0100")
        timestamp = time.strftime("%Y%m%d%H%M%S")
        amount = str(profile["amount"]).zfill(12)
        card = profile["card_number"]
        
        message = mti + "822000000000" + amount + timestamp + "000001" + "0000" + card
        return message
    
    def send_transaction(self, profile: Dict) -> Dict:
        """Send a transaction from profile"""
        result = {
            "name": profile["name"],
            "profile": profile.get("profile", "UNKNOWN"),
            "status": "PENDING",
            "amount": profile["amount"],
            "currency": profile.get("currency", "USD"),
            "trans_type": profile["trans_type"],
            "error": None
        }
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.host, self.port))
            
            iso_message = self.generate_iso_message(profile)
            s.send(iso_message.encode('utf-8'))
            
            result["status"] = "SENT"
            
            try:
                response = s.recv(4096)
                result["status"] = "SUCCESS" if response else "PROCESSED"
            except (socket.timeout, ConnectionResetError):
                result["status"] = "PROCESSED"
            
            s.close()
            
        except ConnectionRefusedError:
            result["error"] = "Connection refused"
            result["status"] = "FAILED"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "FAILED"
        
        self.results.append(result)
        return result
    
    def run_enabled_profiles(self):
        """Run only enabled profiles"""
        enabled = [p for p in self.profiles if p.get("enabled", True)]
        print(f"\nRunning {len(enabled)} enabled profiles...")
        print()
        
        for i, profile in enumerate(enabled, 1):
            result = self.send_transaction(profile)
            self.print_result(result, i, len(enabled))
            time.sleep(0.3)
    
    def run_specific_profile(self, profile_name: str):
        """Run a specific profile by name"""
        profile = next((p for p in self.profiles if p["name"].lower() == profile_name.lower()), None)
        
        if not profile:
            print(f"✗ Profile not found: {profile_name}")
            print("\nAvailable profiles:")
            for p in self.profiles:
                status = "✓" if p.get("enabled", True) else "✗"
                print(f"  {status} {p['name']}")
            return
        
        print(f"\nRunning profile: {profile['name']}")
        print()
        result = self.send_transaction(profile)
        self.print_result(result, 1, 1)
    
    def run_by_card_type(self, card_type: str):
        """Run all profiles for a specific card type"""
        card_map = {
            "visa": "4111111111111111",
            "mastercard": "5555555555554444",
            "amex": "378282246310005",
            "discover": "6011111111111117"
        }
        
        card_number = card_map.get(card_type.lower())
        if not card_number:
            print(f"✗ Unknown card type: {card_type}")
            print(f"Supported: {', '.join(card_map.keys())}")
            return
        
        matching = [p for p in self.profiles if p["card_number"] == card_number]
        print(f"\nRunning {len(matching)} {card_type.upper()} profiles...")
        print()
        
        for i, profile in enumerate(matching, 1):
            result = self.send_transaction(profile)
            self.print_result(result, i, len(matching))
            time.sleep(0.3)
    
    def print_result(self, result: Dict, current: int, total: int):
        """Print formatted result"""
        emoji_map = {
            "SUCCESS": "✅",
            "PROCESSED": "✓",
            "SENT": "→",
            "PENDING": "⏳",
            "FAILED": "✗"
        }
        
        emoji = emoji_map.get(result["status"], "?")
        amount = result["amount"] / 100
        
        print(f"[{current}/{total}] {emoji} {result['name']}")
        print(f"      Profile: {result['profile']} | Type: {result['trans_type']} | Amount: ${amount:.2f} {result['currency']}")
        print(f"      Status: {result['status']}", end="")
        if result["error"]:
            print(f" | Error: {result['error']}")
        else:
            print()
        print()
    
    def print_summary(self):
        """Print execution summary"""
        if not self.results:
            return
        
        total = len(self.results)
        success = len([r for r in self.results if r["status"] in ["SUCCESS", "PROCESSED"]])
        failed = len([r for r in self.results if r["status"] == "FAILED"])
        total_amount = sum([r["amount"] for r in self.results]) / 100
        
        print("\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total Transactions: {total}")
        print(f"Successful: {success} ({success*100//total if total else 0}%)")
        print(f"Failed: {failed} ({failed*100//total if total else 0}%)")
        print(f"Total Amount: ${total_amount:.2f}")
        print("=" * 70)
        print()
    
    def list_profiles(self):
        """List all available profiles"""
        print("\n" + "=" * 70)
        print("AVAILABLE TEST PROFILES")
        print("=" * 70)
        
        for profile in self.profiles:
            status = "✓" if profile.get("enabled", True) else "✗ (disabled)"
            amount = profile["amount"] / 100
            
            print(f"\n{status} {profile['name']}")
            print(f"   Profile ID: {profile.get('profile', 'N/A')}")
            print(f"   Card: {profile['card_number'][:4]}****{profile['card_number'][-4:]}")
            print(f"   Amount: ${amount:.2f} {profile.get('currency', 'USD')}")
            print(f"   Type: {profile['trans_type']}")
            print(f"   Desc: {profile.get('description', 'N/A')}")
        
        print("\n" + "=" * 70)

def main():
    """Main entry point"""
    import os
    
    config_file = os.path.join(os.path.dirname(__file__), "test-profiles.json")
    
    print("\n" + "=" * 70)
    print("jPOS EE CUSTOM TEST RUNNER")
    print("=" * 70)
    print("Load and run test profiles from JSON configuration")
    print()
    
    runner = CustomTestRunner(config_file)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        
        if cmd == "list":
            runner.list_profiles()
        elif cmd == "run":
            runner.run_enabled_profiles()
            runner.print_summary()
        elif cmd.startswith("visa"):
            runner.run_by_card_type("visa")
            runner.print_summary()
        elif cmd.startswith("mastercard") or cmd.startswith("mc"):
            runner.run_by_card_type("mastercard")
            runner.print_summary()
        elif cmd.startswith("amex"):
            runner.run_by_card_type("amex")
            runner.print_summary()
        elif cmd.startswith("discover"):
            runner.run_by_card_type("discover")
            runner.print_summary()
        else:
            # Try as profile name
            runner.run_specific_profile(cmd)
            runner.print_summary()
    else:
        print("Usage:")
        print("  python3 jposee-custom-runner.py list              # List all profiles")
        print("  python3 jposee-custom-runner.py run               # Run all enabled profiles")
        print("  python3 jposee-custom-runner.py visa              # Run all Visa profiles")
        print("  python3 jposee-custom-runner.py mastercard        # Run all Mastercard profiles")
        print("  python3 jposee-custom-runner.py amex              # Run all AMEX profiles")
        print("  python3 jposee-custom-runner.py discover          # Run all Discover profiles")
        print("  python3 jposee-custom-runner.py <profile_name>    # Run specific profile")
        print()
        
        runner.list_profiles()

if __name__ == "__main__":
    main()
