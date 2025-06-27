#!/usr/bin/env python3
"""
Fixed clipboard monitor with proper environment handling
"""
import subprocess
import sqlite3
import time
import os
import sys
from pathlib import Path

class ClipboardMonitor:
    def __init__(self):
        self.db_path = Path.home() / '.clipboard_manager.db'
        self.last_content = ""
        
        # Ensure DISPLAY is set
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'
        
        self.init_database()
    
    def init_database(self):
        """Initialize database connection"""
        try:
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
            print(f"Database ready: {self.db_path}")
        except Exception as e:
            print(f"Database error: {e}")
            sys.exit(1)
    
    def get_clipboard_content(self):
        """Get current clipboard content"""
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return result.stdout
            return ""
        except Exception as e:
            print(f"Clipboard read error: {e}")
            return ""
    
    def detect_content_type(self, content):
        """Detect content type"""
        import re
        content_lower = content.lower().strip()
        
        if re.match(r'https?://', content_lower):
            return 'url'
        elif '@' in content and '.' in content:
            return 'email'
        elif any(kw in content_lower for kw in ['function', 'class', 'def ', 'import ']):
            return 'code'
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            return 'json'
        elif 'select ' in content_lower and 'from ' in content_lower:
            return 'sql'
        else:
            return 'text'
    
    def add_clipboard_entry(self, content):
        """Add clipboard entry to database"""
        if not content.strip() or len(content) > 100000:
            return False
        
        # Check for duplicates
        cursor = self.conn.execute(
            'SELECT id FROM clipboard_entries WHERE content = ? LIMIT 1',
            (content,)
        )
        if cursor.fetchone():
            return False
        
        # Add entry
        content_type = self.detect_content_type(content)
        size_bytes = len(content.encode('utf-8'))
        word_count = len(content.split())
        char_count = len(content)
        
        try:
            self.conn.execute('''
                INSERT INTO clipboard_entries 
                (content, content_type, size_bytes, word_count, char_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (content, content_type, size_bytes, word_count, char_count))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Insert error: {e}")
            return False
    
    def run(self):
        """Main monitoring loop"""
        print("Fixed clipboard monitor started...")
        print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
        
        # Test clipboard access
        test_content = self.get_clipboard_content()
        if test_content:
            print(f"Initial clipboard: {len(test_content)} chars")
            if self.add_clipboard_entry(test_content):
                print("Added initial content")
            self.last_content = test_content
        else:
            print("No initial clipboard content")
        
        while True:
            try:
                current_content = self.get_clipboard_content()
                if current_content and current_content != self.last_content:
                    if self.add_clipboard_entry(current_content):
                        content_type = self.detect_content_type(current_content)
                        print(f"Captured: {len(current_content)} chars ({content_type})")
                        self.last_content = current_content
                
                time.sleep(2)
            except KeyboardInterrupt:
                print("Monitor stopped")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = ClipboardMonitor()
    monitor.run()
