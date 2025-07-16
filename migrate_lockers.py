#!/usr/bin/env python3
"""
Database migration script to update lockers_available field from INTEGER to BOOLEAN
"""

import os
import sys
import sqlite3

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def migrate_lockers_field():
    """Migrate lockers_available field from INTEGER to BOOLEAN"""
    db_path = os.path.join(project_dir, "data", "library.db")
    
    if not os.path.exists(db_path):
        print("Database not found. Please run setup.py first.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if timeslots table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='timeslots'")
        if not cursor.fetchone():
            print("Timeslots table not found. No migration needed.")
            conn.close()
            return True
        
        # Check current schema
        cursor.execute("PRAGMA table_info(timeslots)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        if 'lockers_available' not in columns:
            print("lockers_available column not found. No migration needed.")
            conn.close()
            return True
        
        current_type = columns['lockers_available']
        print(f"Current lockers_available type: {current_type}")
        
        if current_type.upper() == 'BOOLEAN':
            print("Column is already BOOLEAN type. No migration needed.")
            conn.close()
            return True
        
        print("Starting migration...")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create backup of current data
        cursor.execute("""
            CREATE TEMPORARY TABLE timeslots_backup AS 
            SELECT * FROM timeslots
        """)
        
        # Drop and recreate the table with correct schema
        cursor.execute("DROP TABLE timeslots")
        
        cursor.execute('''
            CREATE TABLE timeslots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                duration_months INTEGER NOT NULL DEFAULT 1,
                lockers_available BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Restore data with converted lockers_available values
        cursor.execute("""
            INSERT INTO timeslots 
            (id, name, start_time, end_time, price, duration_months, 
             lockers_available, is_active, created_at, updated_at)
            SELECT 
                id, name, start_time, end_time, price, duration_months,
                CASE WHEN lockers_available > 0 THEN 1 ELSE 0 END as lockers_available,
                is_active, created_at, updated_at
            FROM timeslots_backup
        """)
        
        # Drop temporary table
        cursor.execute("DROP TABLE timeslots_backup")
        
        # Commit transaction
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - lockers_available field changed from INTEGER to BOOLEAN")
        print("   - Values > 0 converted to TRUE, 0 converted to FALSE")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM timeslots")
        count = cursor.fetchone()[0]
        print(f"   - {count} timeslot records migrated")
        
        conn.close()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Library Management System - Lockers Field Migration")
    print("=" * 50)
    
    success = migrate_lockers_field()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now run the application with the updated locker field.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error above and try again.")
