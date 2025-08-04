#!/usr/bin/env python3
"""
Migration script to help transition from the old monolithic structure to the new modular one.
"""

import os
import shutil
import json
from pathlib import Path

def migrate_data():
    """Migrate data from old structure to new structure."""
    print("🔄 Starting migration from monolithic to modular structure...")
    
    # Create necessary directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Migrate query memory files
    old_memory_file = Path("complete_query_memory.json")
    new_memory_file = data_dir / "query_memory.json"
    
    if old_memory_file.exists():
        print(f"📦 Migrating {old_memory_file} to {new_memory_file}")
        shutil.copy2(old_memory_file, new_memory_file)
        print("✅ Query memory migrated successfully")
    else:
        print("ℹ️ No existing query memory found")
    
    # Migrate query vectors
    old_vectors_file = Path("complete_query_vectors.npy")
    new_vectors_file = data_dir / "query_vectors.npy"
    
    if old_vectors_file.exists():
        print(f"📦 Migrating {old_vectors_file} to {new_vectors_file}")
        shutil.copy2(old_vectors_file, new_vectors_file)
        print("✅ Query vectors migrated successfully")
    else:
        print("ℹ️ No existing query vectors found")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        shutil.copy2(env_example, env_file)
        print("✅ .env file created. Please edit it with your credentials.")
    elif env_file.exists():
        print("ℹ️ .env file already exists")
    else:
        print("⚠️ No env.example found. Please create .env file manually.")
    
    print("\n🎉 Migration completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the server: python main.py server")
    print("4. Use the CLI: python main.py cli")

def cleanup_old_files():
    """Clean up old monolithic files (optional)."""
    print("\n🧹 Optional: Clean up old files?")
    response = input("Remove old monolithic files? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        old_files = [
            "api_server.py",
            "client/universal_client.py",
            "client/mcp_client.py",
            "temp.py",
            "api_server.log",
            "complete_query_memory.json",
            "complete_query_vectors.npy"
        ]
        
        for file_path in old_files:
            if Path(file_path).exists():
                try:
                    os.remove(file_path)
                    print(f"🗑️ Removed {file_path}")
                except Exception as e:
                    print(f"⚠️ Could not remove {file_path}: {e}")
        
        print("✅ Cleanup completed")
    else:
        print("ℹ️ Skipping cleanup")

if __name__ == "__main__":
    print("🔄 Subscription Analytics - Migration Tool")
    print("=" * 50)
    
    migrate_data()
    cleanup_old_files()
    
    print("\n🎯 Migration Summary:")
    print("✅ Data files migrated to data/ directory")
    print("✅ Configuration template created")
    print("✅ New modular structure ready")
    print("\n🚀 You can now use the new modular system!")
    print("   python main.py server  # Start API server")
    print("   python main.py cli     # Use CLI") 