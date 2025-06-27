#!/usr/bin/env python3
"""
Simple clipboard manager with reliable text selection
"""
import sqlite3
import subprocess
import os
from pathlib import Path

class SimpleClipboardManager:
    def __init__(self):
        self.db_path = Path.home() / '.clipboard_manager.db'
        self.init_database()
    
    def init_database(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content_type TEXT DEFAULT 'text',
                size_bytes INTEGER DEFAULT 0,
                is_favorite BOOLEAN DEFAULT 0,
                tags TEXT DEFAULT '',
                word_count INTEGER DEFAULT 0,
                char_count INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def get_clipboard_content(self):
        """Get current clipboard content"""
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True, timeout=2)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def set_clipboard_content(self, content):
        """Set clipboard content"""
        try:
            subprocess.run(['xclip', '-selection', 'clipboard'], 
                          input=content, text=True, timeout=2)
            return True
        except:
            return False
    
    def load_entries(self, limit=20):
        """Load clipboard entries"""
        cursor = self.conn.execute('''
            SELECT id, content, timestamp, content_type, size_bytes, is_favorite
            FROM clipboard_entries
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def show_entry_with_selection(self, entry_id, content):
        """Show entry in a way that allows text selection"""
        print("\n" + "="*80)
        print("📋 CLIPBOARD ENTRY - TEXT SELECTION ENABLED")
        print("="*80)
        print("💡 Select text below with your mouse, then Ctrl+C to copy")
        print("💡 This is plain terminal text - selection works normally")
        print("-"*80)
        print(content)
        print("-"*80)
        print("\n🎯 Instructions:")
        print("1. Select any text above with your mouse")
        print("2. Press Ctrl+C to copy selected text")
        print("3. Press Enter when done to continue")
        
        try:
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\nReturning to menu...")
    
    def run_simple_menu(self):
        """Run simple text-based menu"""
        while True:
            os.system('clear')  # Clear screen
            print("📋 SIMPLE CLIPBOARD MANAGER")
            print("="*50)
            
            entries = self.load_entries(10)
            if not entries:
                print("No clipboard entries found.")
                print("\nOptions:")
                print("c - Capture current clipboard")
                print("q - Quit")
            else:
                print(f"Found {len(entries)} recent entries:\n")
                for i, entry in enumerate(entries, 1):
                    entry_id, content, timestamp, content_type, size_bytes, is_favorite = entry
                    preview = content[:60].replace('\n', ' ')
                    if len(content) > 60:
                        preview += "..."
                    star = "⭐" if is_favorite else "  "
                    print(f"{i:2d}. {star} [{content_type:4s}] {preview}")
                
                print("\nOptions:")
                print("1-9  - View entry with text selection")
                print("c    - Capture current clipboard")
                print("r    - Refresh entries")
                print("q    - Quit")
            
            print("-"*50)
            choice = input("Enter choice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'c':
                content = self.get_clipboard_content()
                if content:
                    self.add_clipboard_entry(content)
                    print(f"✅ Captured {len(content)} characters")
                else:
                    print("❌ No clipboard content found")
                input("Press Enter to continue...")
            elif choice == 'r':
                continue  # Refresh by reloading menu
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(entries):
                    entry = entries[idx]
                    self.show_entry_with_selection(entry[0], entry[1])
                else:
                    print("❌ Invalid entry number")
                    input("Press Enter to continue...")
            else:
                print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    def add_clipboard_entry(self, content):
        """Add clipboard entry to database"""
        if not content.strip():
            return False
        
        # Check for duplicates
        cursor = self.conn.execute(
            'SELECT id FROM clipboard_entries WHERE content = ? LIMIT 1',
            (content,)
        )
        if cursor.fetchone():
            return False
        
        # Detect content type
        content_type = 'text'
        if content.startswith('http'):
            content_type = 'url'
        elif '@' in content and '.' in content:
            content_type = 'email'
        elif any(kw in content.lower() for kw in ['function', 'class', 'def ']):
            content_type = 'code'
        
        # Add entry
        size_bytes = len(content.encode('utf-8'))
        word_count = len(content.split())
        char_count = len(content)
        
        self.conn.execute('''
            INSERT INTO clipboard_entries 
            (content, content_type, size_bytes, word_count, char_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, content_type, size_bytes, word_count, char_count))
        self.conn.commit()
        return True

def main():
    """Main entry point"""
    try:
        manager = SimpleClipboardManager()
        manager.run_simple_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
