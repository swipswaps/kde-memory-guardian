#!/usr/bin/env python3
"""
🎯 Intuitive Clipboard Hub
A completely redesigned, user-friendly interface for clipboard management
Focus: Simplicity, Speed, and Intuitive Workflows
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
import re
import webbrowser
import threading
import time

app = Flask(__name__)

# Configuration
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'

class ClipboardHub:
    def __init__(self):
        self.db_path = CLIPBOARD_DB
    
    def get_recent_entries(self, limit=20):
        """Get recent clipboard entries with smart formatting"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT id, content, timestamp, content_hash,
                       length(content) as size,
                       CASE
                           WHEN content LIKE 'http%' THEN 'url'
                           WHEN content LIKE '%@%.%' THEN 'email'
                           WHEN content GLOB '[0-9]*' AND length(content) < 20 THEN 'number'
                           WHEN length(content) > 500 THEN 'large_text'
                           ELSE 'text'
                       END as type
                FROM clipboard_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                # Smart preview generation
                content = entry['content']
                if entry['type'] == 'url':
                    entry['preview'] = content
                    entry['icon'] = '🔗'
                elif entry['type'] == 'email':
                    entry['preview'] = content
                    entry['icon'] = '📧'
                elif entry['type'] == 'number':
                    entry['preview'] = content
                    entry['icon'] = '🔢'
                elif entry['type'] == 'large_text':
                    entry['preview'] = content[:100] + '...' if len(content) > 100 else content
                    entry['icon'] = '📄'
                else:
                    entry['preview'] = content[:80] + '...' if len(content) > 80 else content
                    entry['icon'] = '📝'
                
                # Human-readable timestamp
                try:
                    dt = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    now = datetime.now()
                    diff = now - dt.replace(tzinfo=None)
                    
                    if diff.days > 0:
                        entry['time_ago'] = f"{diff.days}d ago"
                    elif diff.seconds > 3600:
                        entry['time_ago'] = f"{diff.seconds // 3600}h ago"
                    elif diff.seconds > 60:
                        entry['time_ago'] = f"{diff.seconds // 60}m ago"
                    else:
                        entry['time_ago'] = "Just now"
                except:
                    entry['time_ago'] = "Unknown"
                
                entries.append(entry)
            
            conn.close()
            return entries
        except Exception as e:
            print(f"Error getting entries: {e}")
            return []
    
    def search_entries(self, query, limit=50):
        """Smart search with relevance scoring"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            
            # Use FTS if available, otherwise LIKE search
            cursor = conn.execute('''
                SELECT id, content, timestamp, content_hash,
                       length(content) as size
                FROM clipboard_history 
                WHERE content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_stats(self):
        """Get quick stats for dashboard"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute('SELECT COUNT(*) FROM clipboard_history')
            total = cursor.fetchone()[0]
            
            # Recent activity (last 24 hours)
            cursor = conn.execute('''
                SELECT COUNT(*) FROM clipboard_history 
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
            ''')
            recent = cursor.fetchone()[0]
            
            # Database size
            db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
            
            conn.close()
            return {
                'total_entries': total,
                'recent_24h': recent,
                'db_size_mb': round(db_size, 2)
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {'total_entries': 0, 'recent_24h': 0, 'db_size_mb': 0}

hub = ClipboardHub()

@app.route('/')
def main_interface():
    """Main intuitive interface"""
    return render_template_string(MAIN_TEMPLATE)

@app.route('/api/recent')
def api_recent():
    """Get recent entries"""
    limit = request.args.get('limit', 20, type=int)
    entries = hub.get_recent_entries(limit)
    return jsonify(entries)

@app.route('/api/search')
def api_search():
    """Search entries"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = hub.search_entries(query)
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    """Get dashboard stats"""
    return jsonify(hub.get_stats())

@app.route('/api/entry/<int:entry_id>')
def api_entry(entry_id):
    """Get full entry content"""
    try:
        conn = sqlite3.connect(str(hub.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM clipboard_history WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
        conn.close()
        
        if entry:
            return jsonify(dict(entry))
        else:
            return jsonify({'error': 'Entry not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Main HTML Template
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📋 Clipboard Hub - Intuitive & Fast</title>
    <style>
        /* Reset and Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        /* Main Container */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 300;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Quick Stats */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px 25px;
            text-align: center;
            color: white;
            min-width: 120px;
        }
        
        .stat-number {
            font-size: 1.8rem;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        /* Search Section */
        .search-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .search-container {
            position: relative;
            margin-bottom: 20px;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 50px 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 50px;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .search-icon {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.2rem;
            color: #667eea;
        }
        
        /* Quick Actions */
        .quick-actions {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .action-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Content Area */
        .content-area {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        /* Entry List */
        .entry-list {
            display: grid;
            gap: 15px;
        }
        
        .entry-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 2px solid transparent;
        }
        
        .entry-card:hover {
            background: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        .entry-header {
            display: flex;
            align-items: center;
            justify-content: between;
            margin-bottom: 10px;
        }
        
        .entry-icon {
            font-size: 1.5rem;
            margin-right: 12px;
        }
        
        .entry-meta {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.85rem;
            color: #666;
        }
        
        .entry-time {
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 8px;
        }
        
        .entry-size {
            color: #999;
        }
        
        .entry-preview {
            font-size: 1rem;
            line-height: 1.4;
            color: #333;
            margin-top: 8px;
        }
        
        /* Loading States */
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .stats-bar {
                gap: 15px;
            }
            
            .stat-item {
                min-width: 100px;
                padding: 12px 20px;
            }
            
            .search-section,
            .content-area {
                padding: 20px;
            }
            
            .quick-actions {
                justify-content: stretch;
            }
            
            .action-btn {
                flex: 1;
                justify-content: center;
            }
        }
        
        /* Modal for full content */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 90%;
            max-height: 80%;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #999;
            padding: 5px;
        }
        
        .close-btn:hover {
            color: #333;
        }
        
        .modal-text {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.95rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📋 Clipboard Hub</h1>
            <p>Fast, intuitive access to your clipboard history</p>
        </div>
        
        <!-- Quick Stats -->
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-number" id="total-count">-</span>
                <span class="stat-label">Total Entries</span>
            </div>
            <div class="stat-item">
                <span class="stat-number" id="recent-count">-</span>
                <span class="stat-label">Last 24h</span>
            </div>
            <div class="stat-item">
                <span class="stat-number" id="db-size">-</span>
                <span class="stat-label">Database Size</span>
            </div>
        </div>
        
        <!-- Search Section -->
        <div class="search-section">
            <div class="search-container">
                <input type="text" class="search-input" id="search-input" 
                       placeholder="Search your clipboard history...">
                <span class="search-icon">🔍</span>
            </div>
            
            <div class="quick-actions">
                <button class="action-btn" onclick="loadRecent()">
                    📋 Recent Items
                </button>
                <button class="action-btn" onclick="showUrls()">
                    🔗 URLs Only
                </button>
                <button class="action-btn" onclick="showLargeText()">
                    📄 Large Text
                </button>
                <button class="action-btn" onclick="openTools()">
                    🛠️ Advanced Tools
                </button>
            </div>
        </div>
        
        <!-- Content Area -->
        <div class="content-area">
            <div id="content-list" class="entry-list">
                <div class="loading">
                    <div class="spinner"></div>
                    <div>Loading your clipboard history...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal for full content -->
    <div class="modal" id="content-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Full Content</h3>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-text" id="modal-text"></div>
        </div>
    </div>
    
    <script>
        // Global state
        let currentEntries = [];
        let searchTimeout = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadRecent();
            setupSearch();
        });
        
        // Load dashboard stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-count').textContent = stats.total_entries.toLocaleString();
                document.getElementById('recent-count').textContent = stats.recent_24h;
                document.getElementById('db-size').textContent = stats.db_size_mb + ' MB';
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Load recent entries
        async function loadRecent(limit = 20) {
            showLoading();
            try {
                const response = await fetch(`/api/recent?limit=${limit}`);
                const entries = await response.json();
                currentEntries = entries;
                displayEntries(entries);
            } catch (error) {
                showError('Failed to load recent entries');
            }
        }
        
        // Setup search functionality
        function setupSearch() {
            const searchInput = document.getElementById('search-input');
            
            searchInput.addEventListener('input', function(e) {
                const query = e.target.value.trim();
                
                // Clear previous timeout
                if (searchTimeout) {
                    clearTimeout(searchTimeout);
                }
                
                // Debounce search
                searchTimeout = setTimeout(() => {
                    if (query.length > 0) {
                        performSearch(query);
                    } else {
                        loadRecent();
                    }
                }, 300);
            });
            
            // Enter key search
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const query = e.target.value.trim();
                    if (query.length > 0) {
                        performSearch(query);
                    }
                }
            });
        }
        
        // Perform search
        async function performSearch(query) {
            showLoading();
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                currentEntries = results;
                displayEntries(results, `Search results for "${query}"`);
            } catch (error) {
                showError('Search failed');
            }
        }
        
        // Display entries
        function displayEntries(entries, title = 'Recent Clipboard Items') {
            const container = document.getElementById('content-list');
            
            if (entries.length === 0) {
                container.innerHTML = `
                    <div class="loading">
                        <div style="font-size: 2rem; margin-bottom: 15px;">📭</div>
                        <div>No entries found</div>
                    </div>
                `;
                return;
            }
            
            const html = entries.map(entry => `
                <div class="entry-card" onclick="showFullContent(${entry.id})">
                    <div class="entry-header">
                        <div style="display: flex; align-items: center;">
                            <span class="entry-icon">${entry.icon || '📝'}</span>
                            <div class="entry-meta">
                                <span class="entry-time">${entry.time_ago || 'Unknown'}</span>
                                <span class="entry-size">${entry.size} chars</span>
                            </div>
                        </div>
                    </div>
                    <div class="entry-preview">${escapeHtml(entry.preview || entry.content)}</div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }
        
        // Show full content in modal
        async function showFullContent(entryId) {
            try {
                const response = await fetch(`/api/entry/${entryId}`);
                const entry = await response.json();
                
                document.getElementById('modal-text').textContent = entry.content;
                document.getElementById('content-modal').style.display = 'block';
                
                // Copy to clipboard on click
                document.getElementById('modal-text').onclick = function() {
                    navigator.clipboard.writeText(entry.content).then(() => {
                        // Visual feedback
                        this.style.background = '#d4edda';
                        setTimeout(() => {
                            this.style.background = '#f8f9fa';
                        }, 500);
                    });
                };
            } catch (error) {
                console.error('Error loading full content:', error);
            }
        }
        
        // Close modal
        function closeModal() {
            document.getElementById('content-modal').style.display = 'none';
        }
        
        // Quick action functions
        function showUrls() {
            const urls = currentEntries.filter(entry => entry.type === 'url');
            displayEntries(urls, 'URLs from Clipboard');
        }
        
        function showLargeText() {
            const largeText = currentEntries.filter(entry => entry.type === 'large_text');
            displayEntries(largeText, 'Large Text Entries');
        }
        
        function openTools() {
            // Open advanced tools in new tab
            window.open('http://localhost:5000', '_blank');
        }
        
        // Utility functions
        function showLoading() {
            document.getElementById('content-list').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <div>Loading...</div>
                </div>
            `;
        }
        
        function showError(message) {
            document.getElementById('content-list').innerHTML = `
                <div class="loading">
                    <div style="font-size: 2rem; margin-bottom: 15px;">⚠️</div>
                    <div>${message}</div>
                </div>
            `;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Close modal on outside click
        document.getElementById('content-modal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Escape to close modal
            if (e.key === 'Escape') {
                closeModal();
            }
            
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('search-input').focus();
            }
        });
    </script>
</body>
</html>
'''

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1)
    webbrowser.open('http://localhost:4000')

if __name__ == '__main__':
    print("🎯 Starting Intuitive Clipboard Hub...")
    print("=" * 60)
    print("🌟 COMPLETELY REDESIGNED INTERFACE:")
    print("• Clean, modern design focused on usability")
    print("• Instant search with smart previews")
    print("• One-click access to clipboard content")
    print("• Mobile-responsive design")
    print("• Keyboard shortcuts (Ctrl+K for search)")
    print("• Smart content type detection")
    print("• Click any entry to view full content")
    print("• Click content in modal to copy to clipboard")
    print("")
    print("🔗 ACCESS:")
    print("📱 Intuitive Interface: http://localhost:4000")
    print("🛠️ Advanced Tools: http://localhost:5000")
    print("📊 Enhanced Hub: http://localhost:3001")
    print("=" * 60)
    
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=4000, debug=False)
