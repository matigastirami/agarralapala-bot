#!/usr/bin/env python3

import requests
import os
import sys
from datetime import datetime

def ping_service():
    """Single ping to keep Render service alive - designed for cron jobs"""
    
    # Get the service URL from environment variable
    service_url = os.environ.get('RENDER_SERVICE_URL')
    
    if not service_url:
        print("ERROR: RENDER_SERVICE_URL environment variable not set")
        sys.exit(1)
    
    health_endpoint = f"{service_url}/health"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        response = requests.get(health_endpoint, timeout=30)
        
        if response.status_code == 200:
            print(f"[{timestamp}] Keep-alive ping successful: {response.status_code}")
            sys.exit(0)
        else:
            print(f"[{timestamp}] Keep-alive ping returned: {response.status_code}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"[{timestamp}] Keep-alive ping failed: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"[{timestamp}] Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    ping_service()