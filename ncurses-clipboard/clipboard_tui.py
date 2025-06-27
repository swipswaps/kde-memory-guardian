#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# clipboard_tui.py — PRF-COMPOSITE-2025-06-24-NCURSES
# WHO: Lightweight ncurses clipboard manager for low-resource environments
# WHAT: Terminal-based clipboard with fuzzy search, categories, favorites
# WHY: Immune to plasma crashes, minimal RAM usage, works on older hardware
# HOW: Python ncurses with SQLite backend, keyboard-driven interface
################################################################################

import curses
import sqlite3
import json
import subprocess
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import re
import signal

class ClipboardTUI:
    def __init__(self):
        """Initialize the ncurses clipboard manager"""
        self.db_path = Path.home() / '.clipboard_manager.db'
        self.init_database()
        self.current_page = 0
        self.items_per_page = 20
        self.search_query = ""
        self.selected_index = 0
        self.show_help = False
        self.filter_mode = "all"  # all, favorites, recent, urls, code
        self.clipboard_data = []
        self.status_message = ""
        self.status_timeout = 0
        
    def init_database(self):
        """Initialize SQLite database for clipboard storage"""
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
        except Exception as e:
            print(f"Database initialization error: {e}")
            sys.exit(1)
    
    def get_clipboard_content(self):
        """Get current clipboard content using xclip"""
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True, timeout=2)
            return result.stdout if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""
    
    def set_clipboard_content(self, content):
        """Set clipboard content using xclip"""
        try:
            subprocess.run(['xclip', '-selection', 'clipboard'], 
                          input=content, text=True, timeout=2)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def add_clipboard_entry(self, content):
        """Add new clipboard entry to database"""
        if not content.strip():
            return
            
        # Detect content type
        content_type = self.detect_content_type(content)
        size_bytes = len(content.encode('utf-8'))
        word_count = len(content.split())
        char_count = len(content)
        
        # Check if entry already exists (avoid duplicates)
        cursor = self.conn.execute(
            'SELECT id FROM clipboard_entries WHERE content = ? LIMIT 1',
            (content,)
        )
        if cursor.fetchone():
            return
        
        # Insert new entry
        self.conn.execute('''
            INSERT INTO clipboard_entries 
            (content, content_type, size_bytes, word_count, char_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, content_type, size_bytes, word_count, char_count))
        self.conn.commit()
    
    def detect_content_type(self, content):
        """Detect content type for categorization"""
        content_lower = content.lower().strip()
        
        if re.match(r'https?://', content_lower):
            return 'url'
        elif re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            return 'email'
        elif any(keyword in content_lower for keyword in ['function', 'class', 'import', 'def ', 'var ', '{']):
            return 'code'
        elif content.startswith('{') and content.endswith('}'):
            return 'json'
        elif content_lower.startswith('select ') or 'from ' in content_lower:
            return 'sql'
        elif len(content) > 1000:
            return 'document'
        else:
            return 'text'
    
    def load_clipboard_data(self):
        """Load clipboard data based on current filter and search"""
        query = '''
            SELECT id, content, timestamp, content_type, size_bytes, 
                   is_favorite, word_count, char_count
            FROM clipboard_entries
        '''
        params = []
        
        # Apply filters
        conditions = []
        if self.filter_mode == "favorites":
            conditions.append("is_favorite = 1")
        elif self.filter_mode == "recent":
            conditions.append("timestamp >= datetime('now', '-1 day')")
        elif self.filter_mode == "urls":
            conditions.append("content_type = 'url'")
        elif self.filter_mode == "code":
            conditions.append("content_type IN ('code', 'json', 'sql')")
        
        # Apply search
        if self.search_query:
            conditions.append("content LIKE ?")
            params.append(f"%{self.search_query}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([self.items_per_page, self.current_page * self.items_per_page])
        
        cursor = self.conn.execute(query, params)
        self.clipboard_data = cursor.fetchall()
    
    def toggle_favorite(self, entry_id):
        """Toggle favorite status of an entry"""
        cursor = self.conn.execute(
            'SELECT is_favorite FROM clipboard_entries WHERE id = ?',
            (entry_id,)
        )
        result = cursor.fetchone()
        if result:
            new_status = 1 - result[0]
            self.conn.execute(
                'UPDATE clipboard_entries SET is_favorite = ? WHERE id = ?',
                (new_status, entry_id)
            )
            self.conn.commit()
            return new_status
        return False
    
    def delete_entry(self, entry_id):
        """Delete a clipboard entry"""
        self.conn.execute('DELETE FROM clipboard_entries WHERE id = ?', (entry_id,))
        self.conn.commit()
    
    def get_stats(self):
        """Get clipboard statistics"""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN is_favorite = 1 THEN 1 END) as favorites,
                COUNT(CASE WHEN content_type = 'url' THEN 1 END) as urls,
                COUNT(CASE WHEN content_type IN ('code', 'json', 'sql') THEN 1 END) as code,
                SUM(size_bytes) as total_size
            FROM clipboard_entries
        ''')
        return cursor.fetchone()
    
    def set_status(self, message, timeout=3):
        """Set status message with timeout"""
        self.status_message = message
        self.status_timeout = time.time() + timeout

    def import_clipboard_data(self):
        """Force import current clipboard and add sample data if empty"""
        # First try to capture current clipboard
        current_content = self.get_clipboard_content()
        if current_content:
            self.add_clipboard_entry(current_content)
            self.set_status("Imported current clipboard content")

        # Add some sample data if database is still empty
        cursor = self.conn.execute('SELECT COUNT(*) FROM clipboard_entries')
        count = cursor.fetchone()[0]

        if count == 0:
            sample_entries = [
                "https://github.com/swipswaps/clipboard-manager",
                "user@example.com",
                "def hello_world():\n    print('Hello from clipboard!')\n    return True",
                '{"name": "clipboard", "type": "manager", "features": ["search", "favorites"]}',
                "SELECT * FROM clipboard_entries WHERE content_type = 'code';",
                "This is a sample text entry for testing the clipboard manager.",
                "# Markdown Example\n\n## Features\n- Search\n- Favorites\n- Categories"
            ]

            for content in sample_entries:
                self.add_clipboard_entry(content)

            self.set_status(f"Added {len(sample_entries)} sample entries for testing")

        self.load_clipboard_data()

    def export_entry_to_file(self, entry_id, content):
        """Export entry to temporary file for text selection"""
        import tempfile
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_path = f.name

            # Open in default text editor for selection
            subprocess.run(['xdg-open', temp_path], check=False)
            self.set_status(f"Exported to {temp_path} - opened in text editor")
        except Exception as e:
            self.set_status(f"Export failed: {e}", 5)

    def view_raw_text(self, entry_id, content):
        """View raw text in terminal (allows normal text selection)"""
        # Temporarily exit ncurses to allow normal terminal text selection
        curses.endwin()

        try:
            print("\n" + "="*80)
            print("📋 CLIPBOARD ENTRY - RAW TEXT VIEW")
            print("="*80)
            print("💡 You can now select text normally with your mouse!")
            print("💡 Use Ctrl+C to copy selected text, then press Enter to return.")
            print("-"*80)
            print(content)
            print("-"*80)
            print("Press Enter to return to clipboard manager...")

            # Wait for user to press Enter
            input()

        except KeyboardInterrupt:
            pass
        finally:
            # Reinitialize ncurses
            print("Returning to clipboard manager...")
            # The main loop will reinitialize the screen
    
    def draw_header(self, stdscr):
        """Draw header with title and stats"""
        height, width = stdscr.getmaxyx()
        stats = self.get_stats()
        
        # Title
        title = "📋 NCURSES CLIPBOARD MANAGER"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Stats line
        if stats:
            total, favorites, urls, code, total_size = stats
            size_mb = (total_size or 0) / 1024 / 1024
            stats_line = f"Total: {total} | ⭐ {favorites} | 🔗 {urls} | 💻 {code} | 📊 {size_mb:.1f}MB"
            stdscr.addstr(1, (width - len(stats_line)) // 2, stats_line)
        
        # Filter and search info
        filter_info = f"Filter: {self.filter_mode.upper()}"
        if self.search_query:
            filter_info += f" | Search: '{self.search_query}'"
        stdscr.addstr(2, 2, filter_info, curses.A_DIM)
    
    def draw_help(self, stdscr):
        """Draw help panel"""
        height, width = stdscr.getmaxyx()
        help_text = [
            "KEYBOARD SHORTCUTS:",
            "",
            "Navigation:",
            "  ↑/↓ or j/k    - Move selection",
            "  PgUp/PgDn     - Page up/down",
            "  Home/End      - First/last item",
            "",
            "Actions:",
            "  Enter/Space   - Copy to clipboard",
            "  f             - Toggle favorite ⭐",
            "  d             - Delete entry",
            "  c             - Capture current clipboard",
            "  i             - Import/add sample data",
            "  e             - Export to file (for text selection)",
            "  v             - View raw text (allows mouse selection)",
            "",
            "Filters:",
            "  1 - All entries    4 - URLs only",
            "  2 - Favorites ⭐   5 - Code/JSON/SQL",
            "  3 - Recent (24h)",
            "",
            "Search:",
            "  /             - Start search",
            "  Esc           - Clear search",
            "",
            "Other:",
            "  h or ?        - Toggle this help",
            "  r             - Refresh",
            "  q             - Quit",
        ]
        
        start_row = 4
        for i, line in enumerate(help_text):
            if start_row + i < height - 1:
                attr = curses.A_BOLD if line.endswith(":") else curses.A_NORMAL
                stdscr.addstr(start_row + i, 4, line[:width-8], attr)
    
    def draw_entries(self, stdscr):
        """Draw clipboard entries list"""
        height, width = stdscr.getmaxyx()
        start_row = 4

        if not self.clipboard_data:
            stdscr.addstr(start_row + 2, 4, "No clipboard entries found.", curses.A_DIM)
            stdscr.addstr(start_row + 4, 4, "Press 'c' to capture current clipboard content.", curses.A_DIM)
            stdscr.addstr(start_row + 5, 4, "Press 'i' to manually import clipboard data.", curses.A_DIM)
            stdscr.addstr(start_row + 6, 4, "Press 'r' to refresh and check for entries.", curses.A_DIM)
            return
        
        for i, entry in enumerate(self.clipboard_data):
            if start_row + i >= height - 3:
                break
                
            entry_id, content, timestamp, content_type, size_bytes, is_favorite, word_count, char_count = entry
            
            # Highlight selected entry
            attr = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
            
            # Format entry line
            favorite_mark = "⭐" if is_favorite else "  "
            type_icon = {
                'url': '🔗', 'email': '📧', 'code': '💻', 
                'json': '📄', 'sql': '🗃️', 'document': '📝'
            }.get(content_type, '📄')
            
            # Truncate content for display
            display_content = content.replace('\n', ' ').replace('\t', ' ')
            max_content_width = width - 25
            if len(display_content) > max_content_width:
                display_content = display_content[:max_content_width-3] + "..."
            
            # Format timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M')
            
            # Size info
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes//1024}K"
            else:
                size_str = f"{size_bytes//1024//1024}M"
            
            entry_line = f"{favorite_mark}{type_icon} {display_content}"
            info_line = f"[{time_str} {size_str} {word_count}w]"
            
            # Draw entry
            try:
                stdscr.addstr(start_row + i, 2, entry_line[:width-20], attr)
                stdscr.addstr(start_row + i, width - len(info_line) - 2, info_line, attr | curses.A_DIM)
            except curses.error:
                pass  # Ignore if we can't draw at edge of screen
    
    def draw_footer(self, stdscr):
        """Draw footer with status and shortcuts"""
        height, width = stdscr.getmaxyx()
        
        # Status message
        if self.status_message and time.time() < self.status_timeout:
            stdscr.addstr(height - 2, 2, self.status_message[:width-4], curses.A_BOLD)
        else:
            # Show quick shortcuts
            shortcuts = "Enter:Copy | v:RawView | f:Favorite | d:Delete | /:Search | h:Help | q:Quit"
            stdscr.addstr(height - 2, 2, shortcuts[:width-4], curses.A_DIM)
        
        # Page info
        if self.clipboard_data:
            page_info = f"Page {self.current_page + 1} | {len(self.clipboard_data)} items"
            stdscr.addstr(height - 1, width - len(page_info) - 2, page_info, curses.A_DIM)
    
    def handle_search_input(self, stdscr):
        """Handle search input mode"""
        height, width = stdscr.getmaxyx()
        
        # Show search prompt
        prompt = "Search: "
        stdscr.addstr(height - 2, 2, prompt + self.search_query, curses.A_REVERSE)
        stdscr.addstr(height - 2, len(prompt) + len(self.search_query) + 2, "_", curses.A_REVERSE)
        
        while True:
            key = stdscr.getch()
            
            if key == 27:  # Escape
                break
            elif key in (10, 13):  # Enter
                self.load_clipboard_data()
                self.selected_index = 0
                self.current_page = 0
                break
            elif key in (8, 127, curses.KEY_BACKSPACE):  # Backspace
                if self.search_query:
                    self.search_query = self.search_query[:-1]
            elif 32 <= key <= 126:  # Printable characters
                self.search_query += chr(key)
            
            # Update display
            stdscr.addstr(height - 2, 2, " " * (width - 4))  # Clear line
            stdscr.addstr(height - 2, 2, prompt + self.search_query, curses.A_REVERSE)
            stdscr.addstr(height - 2, len(prompt) + len(self.search_query) + 2, "_", curses.A_REVERSE)
            stdscr.refresh()
    
    def run(self, stdscr):
        """Main application loop"""
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(100)  # Non-blocking input with 100ms timeout

        # Enable mouse support for text selection
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
            # Allow terminal's native text selection to work
            stdscr.keypad(True)
        except:
            pass  # Mouse support optional

        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
        
        # Load initial data
        self.load_clipboard_data()
        
        while True:
            # Clear screen and redraw
            stdscr.clear()
            
            if self.show_help:
                self.draw_help(stdscr)
            else:
                self.draw_header(stdscr)
                self.draw_entries(stdscr)
            
            self.draw_footer(stdscr)
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            
            if key == -1:  # Timeout, continue loop
                continue
            elif key == ord('q'):  # Quit
                break
            elif key in (ord('h'), ord('?')):  # Help
                self.show_help = not self.show_help
            elif key == ord('r'):  # Refresh
                self.load_clipboard_data()
                self.set_status("Refreshed clipboard data")
            elif key == ord('/'):  # Search
                if not self.show_help:
                    self.handle_search_input(stdscr)
            elif key == 27:  # Escape - clear search
                if self.search_query:
                    self.search_query = ""
                    self.load_clipboard_data()
                    self.selected_index = 0
                    self.current_page = 0
                    self.set_status("Search cleared")
            elif not self.show_help and self.clipboard_data:
                self.handle_entry_actions(key)
    
    def handle_entry_actions(self, key):
        """Handle actions on clipboard entries"""
        if not self.clipboard_data:
            return
            
        entry = self.clipboard_data[self.selected_index]
        entry_id, content = entry[0], entry[1]
        
        if key in (10, 13, ord(' ')):  # Enter or Space - Copy to clipboard
            if self.set_clipboard_content(content):
                self.set_status(f"Copied {len(content)} characters to clipboard")
            else:
                self.set_status("Failed to copy to clipboard", 5)
        
        elif key == ord('f'):  # Toggle favorite
            new_status = self.toggle_favorite(entry_id)
            status = "Added to favorites" if new_status else "Removed from favorites"
            self.set_status(status)
            self.load_clipboard_data()  # Refresh to show changes
        
        elif key == ord('d'):  # Delete entry
            self.delete_entry(entry_id)
            self.set_status("Entry deleted")
            self.load_clipboard_data()
            if self.selected_index >= len(self.clipboard_data) and self.selected_index > 0:
                self.selected_index -= 1
        
        elif key == ord('c'):  # Capture current clipboard
            current_content = self.get_clipboard_content()
            if current_content:
                self.add_clipboard_entry(current_content)
                self.load_clipboard_data()
                self.set_status("Captured current clipboard content")
            else:
                self.set_status("No clipboard content to capture")

        elif key == ord('i'):  # Import/force capture
            self.import_clipboard_data()

        elif key == ord('e'):  # Export entry to file for text selection
            if self.clipboard_data:
                self.export_entry_to_file(entry_id, content)

        elif key == ord('v'):  # View raw text (allows terminal text selection)
            if self.clipboard_data:
                self.view_raw_text(entry_id, content)
        
        # Navigation
        elif key in (curses.KEY_UP, ord('k')):
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key in (curses.KEY_DOWN, ord('j')):
            if self.selected_index < len(self.clipboard_data) - 1:
                self.selected_index += 1
        elif key == curses.KEY_PPAGE:  # Page Up
            self.selected_index = 0
            if self.current_page > 0:
                self.current_page -= 1
                self.load_clipboard_data()
        elif key == curses.KEY_NPAGE:  # Page Down
            self.selected_index = 0
            self.current_page += 1
            self.load_clipboard_data()
            if not self.clipboard_data:  # No more data
                self.current_page -= 1
                self.load_clipboard_data()
        elif key == curses.KEY_HOME:
            self.selected_index = 0
        elif key == curses.KEY_END:
            self.selected_index = len(self.clipboard_data) - 1
        
        # Filter modes
        elif key == ord('1'):
            self.filter_mode = "all"
            self.load_clipboard_data()
            self.selected_index = 0
            self.current_page = 0
            self.set_status("Showing all entries")
        elif key == ord('2'):
            self.filter_mode = "favorites"
            self.load_clipboard_data()
            self.selected_index = 0
            self.current_page = 0
            self.set_status("Showing favorites only")
        elif key == ord('3'):
            self.filter_mode = "recent"
            self.load_clipboard_data()
            self.selected_index = 0
            self.current_page = 0
            self.set_status("Showing recent entries (24h)")
        elif key == ord('4'):
            self.filter_mode = "urls"
            self.load_clipboard_data()
            self.selected_index = 0
            self.current_page = 0
            self.set_status("Showing URLs only")
        elif key == ord('5'):
            self.filter_mode = "code"
            self.load_clipboard_data()
            self.selected_index = 0
            self.current_page = 0
            self.set_status("Showing code/JSON/SQL only")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    curses.endwin()
    print("\nClipboard TUI terminated.")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        app = ClipboardTUI()
        curses.wrapper(app.run)
    except Exception as e:
        curses.endwin()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        curses.endwin()

if __name__ == "__main__":
    main()
