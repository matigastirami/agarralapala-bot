#!/usr/bin/env python3
"""
Database seeder main script.
Usage: python -m common.database.seeders [--clear]
"""

import argparse
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.database.seeders.candidate_seeder import seed_candidates, clear_candidates


def main():
    parser = argparse.ArgumentParser(description='Database seeder for the jobs-agent application')
    parser.add_argument('--clear', action='store_true', help='Clear all seeded data before seeding')
    parser.add_argument('--clear-only', action='store_true', help='Only clear seeded data, do not seed')
    
    args = parser.parse_args()
    
    if args.clear_only:
        print("🗑️  Clearing seeded candidates...")
        clear_candidates()
        return
    
    if args.clear:
        print("🗑️  Clearing existing seeded candidates...")
        clear_candidates()
    
    print("🌱 Starting database seeding...")
    seed_candidates()
    print("✅ Database seeding completed!")


if __name__ == "__main__":
    main()
