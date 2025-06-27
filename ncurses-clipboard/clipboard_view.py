#!/usr/bin/env python3
"""
Clipboard viewer that displays entries for text selection
"""
import sqlite3
import sys
from pathlib import Path

def load_entries():
    """Load clipboard entries from database"""
    db_path = Path.home() / '.clipboard_manager.db'
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute('''
            SELECT id, content, timestamp, content_type, size_bytes
            FROM clipboard_entries
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        entries = cursor.fetchall()
        conn.close()
        return entries
    except Exception as e:
        print(f"Database error: {e}")
        return []

def show_entry(entry_id):
    """Show specific entry for text selection"""
    db_path = Path.home() / '.clipboard_manager.db'
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            'SELECT content FROM clipboard_entries WHERE id = ?',
            (entry_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            content = result[0]
            print("\n" + "="*80)
            print("📋 CLIPBOARD ENTRY - SELECT TEXT WITH MOUSE")
            print("="*80)
            print("💡 Use your mouse to select any text below")
            print("💡 Press Ctrl+C to copy selected text")
            print("💡 This is normal terminal text - selection works!")
            print("-"*80)
            print(content)
            print("-"*80)
            print("✅ Text selection enabled above ↑")
            print("🖱️ Select with mouse + Ctrl+C to copy")
        else:
            print("Entry not found")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Show specific entry
        try:
            entry_id = int(sys.argv[1])
            show_entry(entry_id)
        except ValueError:
            print("Invalid entry ID")
        return
    
    # Show list of entries
    entries = load_entries()
    if not entries:
        print("No clipboard entries found")
        print("Run 'cb' to use the full clipboard manager")
        return
    
    print("📋 CLIPBOARD ENTRIES - SELECT ANY TO VIEW")
    print("="*60)
    print("💡 Run: python3 clipboard_view.py <number> to view entry")
    print("💡 Example: python3 clipboard_view.py 1")
    print("-"*60)
    
    for i, entry in enumerate(entries, 1):
        entry_id, content, timestamp, content_type, size_bytes = entry
        preview = content[:50].replace('\n', ' ')
        if len(content) > 50:
            preview += "..."
        
        print(f"{i:2d}. [{content_type:4s}] {preview}")
    
    print("-"*60)
    print("🎯 Usage:")
    print(f"   python3 clipboard_view.py 1    # View entry 1")
    print(f"   python3 clipboard_view.py 2    # View entry 2")
    print("   etc.")

if __name__ == "__main__":
    main()
