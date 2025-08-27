#!/usr/bin/env python3
"""
Standalone run script for Crypto Fundraising Monitor
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_fundraising_monitor.main import main

if __name__ == "__main__":
    main() 