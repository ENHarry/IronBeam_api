#!/usr/bin/env python3
"""
Simple Demo Account Reset Script

Reads credentials from .env file and resets the demo account.
"""

import os
import sys
import requests

# Add the python-client to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
python_client_path = os.path.join(current_dir, 'python-client')
sys.path.insert(0, python_client_path)

def main():
    """Main function to reset demo account."""
    
    print("🧰 Simple Demo Account Reset Script")
    print("=" * 50)
    
    # Load credentials from environment variables
    api_key = os.getenv('IRONBEAM_API_KEY')
    username = os.getenv('IRONBEAM_USERNAME')
    password = os.getenv('IRONBEAM_PASSWORD')
    
    if not all([api_key, username, password]):
        print("❌ Missing credentials in environment variables!")
        return
    
    print(f"🔑 Using API Key: {api_key[:10]}...")
    print(f"👤 Username: {username}")
    
    # Define the reset endpoint
    url = "https://demo.ironbeamapi.com/v2/simulatedAccountReset"
    account_id = username  # Assuming account ID is the same as username
    # Prepare the payload
    payload = {
        "api_key": api_key,
        "username": username,
        "password": password
    }
    


    try:
        # Send the reset request
        print("🔄 Sending reset request...")
        response = requests.post(reset_url, json=payload)
        
        if response.status_code == 200:
            print("✅ Demo account reset successfully!")
        else:
            print(f"❌ Failed to reset demo account: {response.text}")
    
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")