#!/usr/bin/env python3

import requests
import time
import os
import logging
from datetime import datetime

def keep_alive():
    """Send keep-alive requests to prevent Render instance from sleeping"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - Keep-Alive - %(levelname)s - %(message)s'
    )
    
    # Get the service URL from environment or use default
    service_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:8000')
    health_endpoint = f"{service_url}/health"
    
    # Keep-alive interval (14 minutes to stay under 15-minute Render timeout)
    interval = 14 * 60  # 14 minutes in seconds
    
    logging.info(f"Starting keep-alive service for {health_endpoint}")
    logging.info(f"Ping interval: {interval} seconds ({interval/60} minutes)")
    
    while True:
        try:
            response = requests.get(health_endpoint, timeout=30)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if response.status_code == 200:
                logging.info(f"[{timestamp}] Keep-alive ping successful: {response.status_code}")
            else:
                logging.warning(f"[{timestamp}] Keep-alive ping returned: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.error(f"[{timestamp}] Keep-alive ping failed: {e}")
        
        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.error(f"[{timestamp}] Unexpected error: {e}")
        
        # Wait for next ping
        time.sleep(interval)

if __name__ == '__main__':
    keep_alive()