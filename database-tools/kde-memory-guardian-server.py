#!/usr/bin/env python3
"""
Enhanced KDE Memory Guardian Database Server
WHO: Users who want superior database tools with excellent UX
WHAT: Multi-database web interface with Adminer integration and enhanced features
WHY: Better than ncurses - professional web interface with all database tools
HOW: Flask server with Adminer, custom tools, and enhanced clipboard integration
"""

import os
import sys
import json
import sqlite3
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, send_file, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'
ADMINER_PATH = BASE_DIR / 'adminer.php'

class DatabaseManager:
    def __init__(self):
        self.databases = {
            'clipboard': {
                'path': str(CLIPBOARD_DB),
                'type': 'sqlite',
                'description': 'Clipboard Manager Database',
                'tables': ['clipboard_history']
            }
        }

    def get_database_info(self, db_name):
        """Get database information"""
        if db_name not in self.databases:
            return None

        db_info = self.databases[db_name].copy()
        if db_info['type'] == 'sqlite' and os.path.exists(db_info['path']):
            try:
                conn = sqlite3.connect(db_info['path'])
                cursor = conn.execute("SELECT COUNT(*) FROM clipboard_history")
                db_info['entry_count'] = cursor.fetchone()[0]

                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                db_info['tables'] = [row[0] for row in cursor.fetchall()]

                # Get database size
                db_info['size_bytes'] = os.path.getsize(db_info['path'])

                # Get recent activity
                cursor = conn.execute("SELECT COUNT(*) FROM clipboard_history WHERE timestamp >= datetime('now', '-24 hours')")
                db_info['recent_entries'] = cursor.fetchone()[0]

                conn.close()
            except Exception as e:
                db_info['error'] = str(e)

        return db_info

    def execute_query(self, db_name, query, params=None):
        """Execute SQL query safely"""
        if db_name not in self.databases:
            return {'error': 'Database not found'}

        db_info = self.databases[db_name]
        if db_info['type'] != 'sqlite':
            return {'error': 'Only SQLite supported currently'}

        try:
            conn = sqlite3.connect(db_info['path'])
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.execute(query, params or [])

            if query.strip().upper().startswith('SELECT'):
                results = [dict(row) for row in cursor.fetchall()]
                return {'success': True, 'data': results, 'count': len(results)}
            else:
                conn.commit()
                return {'success': True, 'affected_rows': cursor.rowcount}
        except Exception as e:
            return {'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def get_quick_stats(self):
        """Get quick database statistics"""
        try:
            conn = sqlite3.connect(str(CLIPBOARD_DB))
            stats = {}

            # Total entries
            cursor = conn.execute("SELECT COUNT(*) FROM clipboard_history")
            stats['total_entries'] = cursor.fetchone()[0]

            # Content types - clipboard_history doesn't have content_type, so we'll analyze content
            stats['content_types'] = {'text': stats['total_entries']}  # Simplified for now

            # Recent activity (last 24 hours)
            cursor = conn.execute("SELECT COUNT(*) FROM clipboard_history WHERE timestamp >= datetime('now', '-24 hours')")
            stats['recent_activity'] = cursor.fetchone()[0]

            # Database size
            stats['db_size_mb'] = round(os.path.getsize(str(CLIPBOARD_DB)) / (1024 * 1024), 2)

            conn.close()
            return stats
        except Exception as e:
            return {'error': str(e)}

db_manager = DatabaseManager()

# Enhanced HTML Template with Material Design
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KDE Memory Guardian - Enhanced Database Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --dark-color: #1e293b;
            --light-color: #f8fafc;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--dark-color);
        }

        .navbar {
            background: rgba(255,255,255,0.95) !important;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .card {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border-radius: 16px;
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), #3b82f6);
            border: none;
            border-radius: 12px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
        }

        .table-container {
            max-height: 500px;
            overflow-y: auto;
            border-radius: 12px;
            background: rgba(255,255,255,0.9);
        }

        .query-editor {
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.9);
            transition: all 0.3s ease;
        }

        .query-editor:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25);
        }

        .stats-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stats-card:hover {
            transform: scale(1.05);
        }

        .stats-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .status-badge {
            border-radius: 20px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.875rem;
        }

        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .tool-button {
            background: rgba(255,255,255,0.9);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 1rem;
            text-decoration: none;
            color: var(--dark-color);
            transition: all 0.3s ease;
            display: block;
            margin-bottom: 0.5rem;
        }

        .tool-button:hover {
            background: rgba(255,255,255,1);
            border-color: var(--primary-color);
            color: var(--primary-color);
            transform: translateX(8px);
        }

        .feature-highlight {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
            border: 2px solid rgba(16, 185, 129, 0.2);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="fas fa-memory me-2 text-primary"></i>KDE Memory Guardian
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/adminer" target="_blank">
                    <i class="fas fa-database me-1"></i>Adminer
                </a>
                <a class="nav-link" href="/tools">
                    <i class="fas fa-tools me-1"></i>Tools
                </a>
                <a class="nav-link" href="/api/docs">
                    <i class="fas fa-book me-1"></i>API
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Quick Stats Row -->
        <div class="row mb-4" id="quick-stats">
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number" id="total-entries">-</div>
                    <div class="text-muted">Total Entries</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number" id="recent-activity">-</div>
                    <div class="text-muted">Recent (24h)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number" id="content-types">-</div>
                    <div class="text-muted">Content Types</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-card">
                    <div class="stats-number" id="db-size">-</div>
                    <div class="text-muted">Database Size</div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-server me-2"></i>Database Status</h5>
                    </div>
                    <div class="card-body" id="database-overview">
                        <div class="text-center py-3">
                            <div class="loading-spinner"></div>
                            <p class="mt-2 text-muted">Loading databases...</p>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-tools me-2"></i>Database Tools</h5>
                    </div>
                    <div class="card-body">
                        <a href="#" class="tool-button" onclick="openAdminer()">
                            <i class="fas fa-database me-2 text-primary"></i>
                            <strong>Adminer</strong><br>
                            <small class="text-muted">Professional database management</small>
                        </a>
                        <a href="#" class="tool-button" onclick="openSQLiteBrowser()">
                            <i class="fas fa-table me-2 text-success"></i>
                            <strong>SQLite Browser</strong><br>
                            <small class="text-muted">Native SQLite GUI tool</small>
                        </a>
                        <a href="#" class="tool-button" onclick="exportDatabase()">
                            <i class="fas fa-download me-2 text-warning"></i>
                            <strong>Export Data</strong><br>
                            <small class="text-muted">Download as JSON/CSV</small>
                        </a>
                        <a href="#" class="tool-button" onclick="generatePlots()">
                            <i class="fas fa-chart-bar me-2 text-info"></i>
                            <strong>Generate Plots</strong><br>
                            <small class="text-muted">Data visualization</small>
                        </a>
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                <div class="card mb-4">
                    <div class="card-header bg-dark text-white">
                        <h5 class="mb-0"><i class="fas fa-terminal me-2"></i>SQL Query Interface</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Database:</label>
                            <select class="form-select" id="database-select">
                                <option value="clipboard">Clipboard Database</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">SQL Query:</label>
                            <textarea class="form-control query-editor" id="sql-query" rows="5"
                                placeholder="Enter your SQL query here...">SELECT * FROM clipboard_history ORDER BY timestamp DESC LIMIT 10;</textarea>
                        </div>
                        <div class="d-flex gap-2 flex-wrap">
                            <button class="btn btn-primary" onclick="executeQuery()">
                                <i class="fas fa-play me-2"></i>Execute Query
                            </button>
                            <button class="btn btn-outline-secondary" onclick="clearQuery()">
                                <i class="fas fa-eraser me-2"></i>Clear
                            </button>
                            <button class="btn btn-outline-info" onclick="loadSampleQueries()">
                                <i class="fas fa-lightbulb me-2"></i>Sample Queries
                            </button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-table me-2"></i>Query Results</h5>
                    </div>
                    <div class="card-body">
                        <div id="query-results">
                            <div class="text-center py-4 text-muted">
                                <i class="fas fa-info-circle me-2"></i>Execute a query to see results
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load quick stats
        async function loadQuickStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();

                document.getElementById('total-entries').textContent = stats.total_entries || 0;
                document.getElementById('recent-activity').textContent = stats.recent_activity || 0;
                document.getElementById('content-types').textContent = Object.keys(stats.content_types || {}).length;
                document.getElementById('db-size').textContent = (stats.db_size_mb || 0) + ' MB';
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        // Load database overview
        async function loadDatabaseOverview() {
            try {
                const response = await fetch('/api/databases');
                const databases = await response.json();

                let html = '';
                for (const [name, info] of Object.entries(databases)) {
                    const statusClass = info.error ? 'danger' : 'success';
                    const statusIcon = info.error ? 'exclamation-triangle' : 'check-circle';

                    html += `
                        <div class="mb-3 p-3 border rounded-3" style="background: rgba(255,255,255,0.5);">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0 fw-semibold">${info.description || name}</h6>
                                <span class="status-badge bg-${statusClass} text-white">
                                    <i class="fas fa-${statusIcon} me-1"></i>
                                    ${info.error ? 'Error' : 'Active'}
                                </span>
                            </div>
                            <div class="small text-muted">
                                ${info.error || `${info.entry_count || 0} entries • ${(info.size_bytes/1024).toFixed(1)} KB • ${info.recent_entries || 0} recent`}
                            </div>
                        </div>
                    `;
                }

                document.getElementById('database-overview').innerHTML = html;
            } catch (error) {
                document.getElementById('database-overview').innerHTML =
                    '<div class="alert alert-danger">Failed to load database info</div>';
            }
        }

        // Execute SQL query
        async function executeQuery() {
            const database = document.getElementById('database-select').value;
            const query = document.getElementById('sql-query').value.trim();

            if (!query) {
                alert('Please enter a SQL query');
                return;
            }

            const resultsContainer = document.getElementById('query-results');
            resultsContainer.innerHTML = '<div class="text-center py-3"><div class="loading-spinner"></div><p class="mt-2">Executing query...</p></div>';

            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ database, query })
                });

                const result = await response.json();
                displayQueryResults(result);
            } catch (error) {
                displayQueryResults({ error: 'Network error: ' + error.message });
            }
        }

        // Display query results
        function displayQueryResults(result) {
            const container = document.getElementById('query-results');

            if (result.error) {
                container.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>${result.error}</div>`;
                return;
            }

            if (result.data && result.data.length > 0) {
                const columns = Object.keys(result.data[0]);
                let html = `
                    <div class="table-responsive table-container">
                        <table class="table table-striped table-hover mb-0">
                            <thead class="table-dark">
                                <tr>${columns.map(col => `<th class="fw-semibold">${col}</th>`).join('')}</tr>
                            </thead>
                            <tbody>
                `;

                result.data.forEach(row => {
                    html += '<tr>';
                    columns.forEach(col => {
                        let value = row[col];
                        if (typeof value === 'string' && value.length > 100) {
                            value = value.substring(0, 100) + '...';
                        }
                        html += `<td>${value || ''}</td>`;
                    });
                    html += '</tr>';
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                    <div class="mt-3 p-2 bg-light rounded">
                        <i class="fas fa-info-circle me-1 text-primary"></i>
                        <strong>${result.count}</strong> rows returned
                    </div>
                `;

                container.innerHTML = html;
            } else if (result.success) {
                container.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check me-2"></i>
                        Query executed successfully. <strong>${result.affected_rows || 0}</strong> rows affected.
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>No results returned</div>';
            }
        }

        // Utility functions
        function clearQuery() {
            document.getElementById('sql-query').value = '';
        }

        function loadSampleQueries() {
            const samples = [
                'SELECT * FROM clipboard_history ORDER BY timestamp DESC LIMIT 10;',
                'SELECT COUNT(*) as total_entries FROM clipboard_history;',
                'SELECT * FROM clipboard_history WHERE content LIKE "%http%" ORDER BY timestamp DESC;',
                'SELECT id, length(content) as size, substr(content, 1, 100) as preview FROM clipboard_history ORDER BY timestamp DESC LIMIT 20;',
                'SELECT DATE(timestamp) as date, COUNT(*) as entries FROM clipboard_history GROUP BY DATE(timestamp) ORDER BY date DESC;'
            ];

            const query = samples[Math.floor(Math.random() * samples.length)];
            document.getElementById('sql-query').value = query;
        }

        function openAdminer() {
            window.open('/adminer', '_blank');
        }

        function openSQLiteBrowser() {
            fetch('/api/open-sqlite-browser', { method: 'POST' });
        }

        function exportDatabase() {
            window.open('/api/export/clipboard', '_blank');
        }

        function generatePlots() {
            fetch('/api/generate-plots', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Plots generated successfully! Check the database-tools directory.');
                    } else {
                        alert('Error generating plots: ' + data.error);
                    }
                });
        }

        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadQuickStats();
            loadDatabaseOverview();
        });

        // Auto-refresh stats every 30 seconds
        setInterval(function() {
            loadQuickStats();
            loadDatabaseOverview();
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(MAIN_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    """Get quick database statistics"""
    return jsonify(db_manager.get_quick_stats())

@app.route('/api/databases')
def get_databases():
    """Get database information"""
    result = {}
    for name in db_manager.databases:
        result[name] = db_manager.get_database_info(name)
    return jsonify(result)

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute SQL query"""
    data = request.get_json()
    database = data.get('database', 'clipboard')
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    result = db_manager.execute_query(database, query)
    return jsonify(result)

@app.route('/api/export/<database>')
def export_database(database):
    """Export database as JSON"""
    if database not in db_manager.databases:
        return jsonify({'error': 'Database not found'}), 404

    result = db_manager.execute_query(database, 'SELECT * FROM clipboard_history ORDER BY timestamp DESC')
    if result.get('error'):
        return jsonify(result), 500

    return jsonify({
        'database': database,
        'exported_at': time.time(),
        'count': len(result['data']),
        'data': result['data']
    })

@app.route('/api/open-sqlite-browser', methods=['POST'])
def open_sqlite_browser():
    """Open SQLite Browser with clipboard database"""
    try:
        subprocess.Popen(['sqlitebrowser', str(CLIPBOARD_DB)])
        return jsonify({'success': True, 'message': 'SQLite Browser opened'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-plots', methods=['POST'])
def generate_plots():
    """Generate data visualization plots"""
    try:
        # Try to run clipboard-plot command
        result = subprocess.run(['clipboard-plot', 'dashboard', '--save'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Plots generated successfully'})
        else:
            return jsonify({'success': False, 'error': result.stderr or 'Plot generation failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/adminer')
def adminer_redirect():
    """Redirect to Adminer with SQLite database"""
    if not ADMINER_PATH.exists():
        return "Adminer not found. Please ensure adminer.php is in the database-tools directory.", 404

    # Start PHP built-in server for Adminer if not running
    start_php_server()
    return redirect('http://localhost:8080/adminer.php?sqlite=' + str(CLIPBOARD_DB))

@app.route('/tools')
def tools_page():
    """Tools and utilities page"""
    tools_html = """
    <div class="container mt-4">
        <h2><i class="fas fa-tools me-2"></i>Database Tools & Utilities</h2>
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><h5>GUI Tools</h5></div>
                    <div class="card-body">
                        <a href="/adminer" target="_blank" class="btn btn-primary mb-2 w-100">
                            <i class="fas fa-database me-2"></i>Adminer (Web Interface)
                        </a>
                        <button onclick="openSQLiteBrowser()" class="btn btn-success mb-2 w-100">
                            <i class="fas fa-table me-2"></i>SQLite Browser (Native)
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><h5>Command Line Tools</h5></div>
                    <div class="card-body">
                        <code>clipboard-sql list</code><br>
                        <code>clipboard-sql show 5</code><br>
                        <code>clipboard-plot dashboard</code><br>
                        <code>cbv 8</code>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return tools_html

@app.route('/api/docs')
def api_docs():
    """API documentation"""
    docs = {
        'title': 'KDE Memory Guardian Database API',
        'version': '2.0.0',
        'description': 'Enhanced database management API with superior UX',
        'endpoints': {
            'GET /': 'Main dashboard interface',
            'GET /api/stats': 'Get quick database statistics',
            'GET /api/databases': 'Get database information',
            'POST /api/query': 'Execute SQL query',
            'GET /api/export/<database>': 'Export database as JSON',
            'POST /api/open-sqlite-browser': 'Open SQLite Browser',
            'POST /api/generate-plots': 'Generate data visualization plots',
            'GET /adminer': 'Access Adminer interface',
            'GET /tools': 'Tools and utilities page',
            'GET /api/docs': 'This documentation'
        },
        'features': [
            'Material Design UI with enhanced UX',
            'Real-time database statistics',
            'Multiple database tool integration',
            'Advanced SQL query interface',
            'Data visualization capabilities',
            'Export functionality',
            'Professional database management'
        ]
    }
    return jsonify(docs)

def start_php_server():
    """Start PHP built-in server for Adminer"""
    def run_php():
        try:
            subprocess.run([
                'php', '-S', 'localhost:8080', '-t', str(BASE_DIR)
            ], capture_output=True)
        except:
            pass

    # Start in background thread
    threading.Thread(target=run_php, daemon=True).start()

if __name__ == '__main__':
    print("🗃️ KDE Memory Guardian - Enhanced Database Manager")
    print("=" * 70)
    print(f"🚀 Main Interface: http://localhost:5000")
    print(f"🗄️ Adminer Access: http://localhost:5000/adminer")
    print(f"🛠️ Tools Page: http://localhost:5000/tools")
    print(f"📚 API Documentation: http://localhost:5000/api/docs")
    print(f"📋 Clipboard Database: {CLIPBOARD_DB}")
    print("=" * 70)

    # Check if clipboard database exists
    if CLIPBOARD_DB.exists():
        size_mb = round(CLIPBOARD_DB.stat().st_size / (1024 * 1024), 2)
        print(f"✅ Clipboard database found ({size_mb} MB)")

        # Get quick stats
        stats = db_manager.get_quick_stats()
        if 'error' not in stats:
            print(f"📊 Database contains {stats.get('total_entries', 0)} entries")
            print(f"📈 Recent activity: {stats.get('recent_activity', 0)} entries in last 24h")
            print(f"📂 Content types: {len(stats.get('content_types', {}))}")
    else:
        print("⚠️ Clipboard database not found - will be created when first used")

    # Check if Adminer exists
    if ADMINER_PATH.exists():
        size_kb = round(ADMINER_PATH.stat().st_size / 1024, 1)
        print(f"✅ Adminer ready ({size_kb} KB)")
    else:
        print("⚠️ Adminer not found - download from https://www.adminer.org/")

    # Check available tools
    tools_available = []
    try:
        subprocess.run(['sqlitebrowser', '--version'], capture_output=True, timeout=2)
        tools_available.append("SQLite Browser")
    except:
        pass

    try:
        subprocess.run(['clipboard-plot', '--help'], capture_output=True, timeout=2)
        tools_available.append("Clipboard Plot")
    except:
        pass

    try:
        subprocess.run(['clipboard-sql', 'help'], capture_output=True, timeout=2)
        tools_available.append("Clipboard SQL")
    except:
        pass

    if tools_available:
        print(f"🔧 Available tools: {', '.join(tools_available)}")

    print("\n🌟 ENHANCED FEATURES:")
    print("• Material Design UI with superior UX")
    print("• Real-time database statistics")
    print("• Multiple database tool integration")
    print("• Advanced SQL query interface")
    print("• Data visualization capabilities")
    print("• Professional database management")

    print(f"\n🚀 Starting enhanced database server...")
    print("💡 Press Ctrl+C to stop the server")

    # Auto-open browser
    try:
        threading.Timer(2.0, lambda: webbrowser.open('http://localhost:5000')).start()
        print("🌐 Opening browser automatically...")
    except:
        pass

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)