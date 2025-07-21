#!/usr/bin/env python3
"""
Script to clean up the repository by removing unwanted files and folders
"""
import os
import shutil
import sys

def clean_repository(repo_path):
    """Remove unwanted files and folders from the repository"""
    # Files and folders to remove
    to_remove = [
        # Temporary and cache files
        "__pycache__",
        ".pytest_cache",
        
        # Vector stores (should be regenerated, not stored in git)
        "faiss_index_ollama",
        "faiss_index_openai",
        "vectorstore_nomic",
        "vectorstore_ollama",
        "vectorstore_openai",
        
        # Uploaded documents (user data, should not be in git)
        "uploads",
        
        # Database files
        "agent_logs.db",
        
        # Temporary or duplicate files
        "enhanced_main.py",
        "run_app.py",
        
        # Logs and generated data
        "feedback_log.jsonl",
        "llm_finetune_data.jsonl",
        "openai_finetune_ready.jsonl"
    ]
    
    # Process each item
    removed = []
    for item in to_remove:
        item_path = os.path.join(repo_path, item)
        if os.path.exists(item_path):
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                removed.append(item)
                print(f"✅ Removed: {item}")
            except Exception as e:
                print(f"❌ Error removing {item}: {str(e)}")
    
    # Update .gitignore to ensure these files don't get added back
    update_gitignore(repo_path, to_remove)
    
    return removed

def update_gitignore(repo_path, items):
    """Update .gitignore to include all removed items"""
    gitignore_path = os.path.join(repo_path, ".gitignore")
    
    # Check if .gitignore exists
    if not os.path.exists(gitignore_path):
        print(f"⚠️ .gitignore not found at {gitignore_path}")
        return
    
    # Read existing .gitignore
    with open(gitignore_path, "r") as f:
        content = f.read()
    
    # Add new entries
    new_entries = []
    for item in items:
        if item not in content:
            if os.path.isdir(os.path.join(repo_path, item)):
                new_entries.append(f"{item}/")
            else:
                new_entries.append(item)
    
    # Append to .gitignore if there are new entries
    if new_entries:
        with open(gitignore_path, "a") as f:
            f.write("\n# Added by cleanup script\n")
            for entry in new_entries:
                f.write(f"{entry}\n")
        print(f"✅ Updated .gitignore with {len(new_entries)} new entries")

if __name__ == "__main__":
    # Get the repository root path (not the scripts directory)
    repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    removed = clean_repository(repo_path)
    print(f"\nRepository cleanup complete. Removed {len(removed)} items.")
    print("Run 'git status' to see changes and commit them.")