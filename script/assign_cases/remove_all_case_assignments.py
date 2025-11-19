#!/usr/bin/env python3
"""
Independent script to selectively remove case assignments from the platform.

This script connects directly to the PostgreSQL database and removes records
from the display_config table, while keeping assignments for specified users.

Usage:
    python script/assign_cases/remove_all_case_assignments.py

Note: This operation is irreversible. Make sure to backup your database before running.
"""

import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
import pandas as pd


# --- DB config from env ---
DB_TYPE = "postgresql"
DB_USER = os.getenv("POSTGRES_USER", "augmed")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "augmed")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "augmed")

CONN_STR = f"{DB_TYPE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Users to keep (their assignments will NOT be removed) ---
USERS_TO_KEEP = [
    'srfort@unc.live.edu',
    'lirjiao@unc.edu', 
    'test123@unc.edu'
]


def get_assignment_statistics(engine):
    """Get current case assignment statistics."""
    query = """
    SELECT 
        user_email,
        case_id,
        id
    FROM display_config
    ORDER BY user_email, case_id;
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return {
                'total_assignments': 0,
                'unique_users': 0,
                'unique_cases': 0,
                'user_assignments': {}
            }
        
        # Calculate statistics
        user_assignments = df.groupby('user_email')['case_id'].apply(list).to_dict()
        
        return {
            'total_assignments': len(df),
            'unique_users': df['user_email'].nunique(),
            'unique_cases': df['case_id'].nunique(),
            'user_assignments': user_assignments
        }
        
    except Exception as e:
        print(f"❌ Error getting statistics: {str(e)}")
        return {
            'total_assignments': 0,
            'unique_users': 0,
            'unique_cases': 0,
            'user_assignments': {}
        }


def display_assignment_summary(stats):
    """Display a summary of case assignments."""
    print("=" * 60)
    print("📊 CASE ASSIGNMENT SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total assignments: {stats['total_assignments']}")
    print(f"Unique users with assignments: {stats['unique_users']}")
    print(f"Unique cases assigned: {stats['unique_cases']}")
    
    # Show which users will be kept
    print(f"\n🔒 USERS TO KEEP (assignments will NOT be removed):")
    kept_count = 0
    for user in USERS_TO_KEEP:
        if user in stats['user_assignments']:
            case_count = len(stats['user_assignments'][user])
            print(f"   ✅ {user:<30} ({case_count} cases)")
            kept_count += case_count
        else:
            print(f"   ⚪ {user:<30} (0 cases)")
    
    print(f"\n📊 REMOVAL IMPACT:")
    print(f"   - Assignments to be removed: {stats['total_assignments'] - kept_count}")
    print(f"   - Assignments to be kept: {kept_count}")
    
    if stats['total_assignments'] == 0:
        print("\n✅ No case assignments found.")
        return False
    
    print("\n📈 DETAILED BREAKDOWN")
    print("-" * 40)
    
    # Users with assignments
    if stats['user_assignments']:
        print("\n👥 Users with assignments:")
        sorted_users = sorted(
            stats['user_assignments'].items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )
        
        for i, (user_email, case_ids) in enumerate(sorted_users[:10]):  # Show top 10
            print(f"   {i+1:2d}. {user_email:<30} ({len(case_ids)} cases)")
        
        if len(sorted_users) > 10:
            print(f"   ... and {len(sorted_users) - 10} more users")
        
        # Assignment distribution
        assignment_counts = [len(cases) for cases in stats['user_assignments'].values()]
        avg_assignments = sum(assignment_counts) / len(assignment_counts)
        max_assignments = max(assignment_counts)
        min_assignments = min(assignment_counts)
        
        print(f"\n📊 Assignment distribution:")
        print(f"   Average assignments per user: {avg_assignments:.1f}")
        print(f"   Maximum assignments per user: {max_assignments}")
        print(f"   Minimum assignments per user: {min_assignments}")
    
    return True


def backup_assignments_to_csv(stats, filename=None):
    """Backup current assignments to a CSV file before removal."""
    if stats['total_assignments'] == 0:
        return None
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"case_assignments_backup_{timestamp}.csv"
    
    try:
        # Create backup CSV in the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        # Prepare data for CSV
        rows = []
        for user_email, case_ids in stats['user_assignments'].items():
            for case_id in case_ids:
                rows.append({
                    'User': user_email,
                    'Case No.': case_id,
                    'Path': '',
                    'Collapse': 'FALSE',
                    'Highlight': 'TRUE',
                    'Top': ''
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        
        print(f"📄 Backup created: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Failed to create backup: {str(e)}")
        return None


def remove_selective_case_assignments(engine):
    """Remove case assignments from the database, keeping specified users."""
    try:
        with engine.begin() as conn:
            # Build the WHERE clause to exclude users we want to keep
            users_to_keep_str = "', '".join(USERS_TO_KEEP)
            query = f"DELETE FROM display_config WHERE user_email NOT IN ('{users_to_keep_str}')"
            
            print(f"🔍 Executing query: {query}")
            result = conn.execute(text(query))
            deleted_count = result.rowcount
            
        print(f"✅ Successfully removed {deleted_count} case assignments!")
        print(f"✅ Kept assignments for users: {', '.join(USERS_TO_KEEP)}")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error removing case assignments: {str(e)}")
        raise


def main():
    """Main function to run the script."""
    print("🚀 Case Assignment Removal Tool")
    print("=" * 60)
    
    # Create database connection
    try:
        engine = create_engine(CONN_STR)
        print("✅ Connected to database successfully")
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        print(f"Connection string: {CONN_STR}")
        return
    
    # Get current statistics
    print("\n🔍 Checking current case assignment statistics...")
    before_stats = get_assignment_statistics(engine)
    
    has_assignments = display_assignment_summary(before_stats)
    
    if not has_assignments:
        print("\n✅ No case assignments found. Nothing to remove.")
        return
    
    # Calculate assignments to be removed
    kept_count = sum(len(before_stats['user_assignments'].get(user, [])) for user in USERS_TO_KEEP)
    to_remove_count = before_stats['total_assignments'] - kept_count
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will remove {to_remove_count} case assignments!")
    print(f"   {kept_count} assignments for specified users will be KEPT.")
    print("   This action is IRREVERSIBLE.")
    
    # Ask if user wants to create a backup
    backup_choice = input("\n💾 Would you like to create a backup CSV file first? (Y/n): ")
    backup_file = None
    
    if backup_choice.lower() not in ['n', 'no']:
        print("\n📄 Creating backup...")
        backup_file = backup_assignments_to_csv(before_stats)
        if backup_file:
            print(f"✅ Backup saved to: {backup_file}")
        else:
            proceed = input("⚠️  Backup failed. Continue anyway? (y/N): ")
            if proceed.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled.")
                return
    
    # Final confirmation
    confirmation = input(f"\n🤔 Are you sure you want to remove {to_remove_count} assignments (keeping {kept_count})? Type 'YES' to continue: ")
    
    if confirmation != 'YES':
        print("❌ Operation cancelled. No changes made.")
        return
    
    print("\n🗑️  Removing all case assignments...")
    
    try:
        deleted_count = remove_selective_case_assignments(engine)
        
        # Verify removal
        print("\n🔍 Verifying removal...")
        after_stats = get_assignment_statistics(engine)
        
        print("\n" + "=" * 60)
        print("📊 REMOVAL SUMMARY")
        print("=" * 60)
        print(f"Assignments removed: {deleted_count}")
        print(f"Assignments remaining: {after_stats['total_assignments']}")
        
        if after_stats['total_assignments'] == 0:
            print("✅ SUCCESS: All case assignments have been removed!")
        else:
            print(f"⚠️  WARNING: {after_stats['total_assignments']} assignments still remain!")
        
        if backup_file:
            print(f"\n💾 Backup file available at: {backup_file}")
        
    except Exception as e:
        print(f"❌ Failed to remove case assignments: {str(e)}")
        return
    
    print("\n🎉 Process completed!")


if __name__ == "__main__":
    main()