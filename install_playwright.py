#!/usr/bin/env python3
"""
Script to install Playwright browsers for job enrichment functionality.
Run this script after installing the requirements to ensure Playwright browsers are available.
"""

import subprocess
import sys

def install_playwright_browsers():
    """Install Playwright browsers"""
    try:
        print("Installing Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully!")
        else:
            print(f"❌ Error installing Playwright browsers: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = install_playwright_browsers()
    if success:
        print("\n🎉 Setup complete! You can now run the job enrichment workflow.")
    else:
        print("\n💥 Setup failed. Please check the error messages above.")
        sys.exit(1)
