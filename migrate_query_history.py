"""
Migration script to transition from local file storage to cloud storage.
Run this script to migrate existing query history to your preferred cloud backend.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from query_history import QueryHistoryManager  # Old version
from query_history_cloud import CloudQueryHistoryManager, FirestoreBackend, CloudSQLBackend

def migrate_local_to_cloud(source_file: str = "query_history.json", target_backend: str = "firestore"):
    """Migrate query history from local file to cloud storage."""
    
    print("🚀 Starting Query History Migration")
    print("=" * 50)
    
    # Load existing data
    source_path = Path(source_file)
    if not source_path.exists():
        print(f"❌ Source file {source_file} not found. Nothing to migrate.")
        return
    
    print(f"📂 Loading data from {source_file}")
    with open(source_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    if not existing_data:
        print("📭 No data found in source file.")
        return
    
    print(f"📊 Found {len(existing_data)} queries to migrate")
    
    # Create target backend
    print(f"🎯 Setting up {target_backend} backend")
    if target_backend == "firestore":
        if not os.getenv('GOOGLE_CLOUD_PROJECT'):
            print("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
            return
        target_manager = CloudQueryHistoryManager(FirestoreBackend())
    elif target_backend == "cloudsql":
        if not os.getenv('DATABASE_URL'):
            print("❌ DATABASE_URL environment variable not set")
            return
        target_manager = CloudQueryHistoryManager(CloudSQLBackend())
    else:
        print(f"❌ Unknown backend type: {target_backend}")
        return
    
    # Migrate data
    print("📤 Migrating data...")
    success_count = 0
    
    for i, query in enumerate(existing_data, 1):
        try:
            # The cloud version expects the data in a specific format
            # Add the query directly to maintain the full structure
            current_history = target_manager.backend.load_history()
            current_history.append(query)
            target_manager.backend.save_history(current_history)
            success_count += 1
            print(f"  ✅ Migrated query {i}/{len(existing_data)}")
        except Exception as e:
            print(f"  ❌ Failed to migrate query {i}: {e}")
    
    print(f"✅ Migration completed: {success_count}/{len(existing_data)} queries migrated")
    
    # Create backup
    backup_path = f"{source_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"💾 Creating backup: {backup_path}")
    source_path.rename(backup_path)
    
    print("🎉 Migration finished!")
    print(f"📁 Original file backed up to: {backup_path}")
    print(f"☁️  Data now stored in {target_backend}")

def verify_migration(backend_type: str = "firestore"):
    """Verify the migration was successful."""
    print("🔍 Verifying migration...")
    
    if backend_type == "firestore":
        manager = CloudQueryHistoryManager(FirestoreBackend())
    elif backend_type == "cloudsql":
        manager = CloudQueryHistoryManager(CloudSQLBackend())
    else:
        print(f"❌ Unknown backend type: {backend_type}")
        return
    
    history = manager.backend.load_history()
    print(f"📊 Found {len(history)} queries in {backend_type}")
    
    if history:
        print("📋 Recent queries:")
        manager.print_recent_queries(3)
    else:
        print("📭 No queries found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate query history to cloud storage")
    parser.add_argument("--source", default="query_history.json", help="Source file path")
    parser.add_argument("--backend", choices=["firestore", "cloudsql"], default="firestore", 
                       help="Target backend type")
    parser.add_argument("--verify", action="store_true", help="Verify migration only")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration(args.backend)
    else:
        migrate_local_to_cloud(args.source, args.backend)
