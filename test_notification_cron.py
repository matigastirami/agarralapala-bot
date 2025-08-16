#!/usr/bin/env python3
"""
Test script for the notification cron
This script allows you to test the notification cron functionality directly
"""

import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crons.notification_cron import NotificationCron

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to test the notification cron"""
    try:
        print("🚀 Starting Notification Cron Test")
        print("=" * 50)
        
        # Create and run the notification cron
        notification_cron = NotificationCron()
        
        print(f"Cron Name: {notification_cron.name}")
        print(f"Interval Hours: {notification_cron.interval_hours}")
        print(f"Start Time: {notification_cron.start_time}")
        print("-" * 50)
        
        # Run the notification process
        print("Running notification process...")
        notification_cron.run()
        
        print("✅ Notification cron test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running notification cron: {str(e)}")
        logging.error(f"Notification cron test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
