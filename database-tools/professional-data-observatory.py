#!/usr/bin/env python3
"""
🏢 Professional Data Observatory
Enterprise-grade data correlation and visualization platform
Inspired by Grafana, Kibana, and Splunk UX patterns

Features:
- Timeline correlation across multiple data sources
- Professional dashboard design patterns
- Data source integration (clipboard, browser, logs, system events)
- Advanced filtering and search capabilities
- Contextual data relationships
- Professional observability patterns (RED/USE methods)
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
import os
import glob
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import threading
import time
import webbrowser

app = Flask(__name__)

# Configuration
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'
BROWSER_HISTORY_PATHS = [
    Path.home() / '.mozilla/firefox/*/places.sqlite',
    Path.home() / '.config/google-chrome/Default/History',
    Path.home() / '.config/chromium/Default/History'
]

class DataObservatory:
    def __init__(self):
        self.clipboard_db = CLIPBOARD_DB
        self.data_sources = {
            'clipboard': {'name': 'Clipboard History', 'icon': '📋', 'color': '#6366f1'},
            'browser': {'name': 'Browser History', 'icon': '🌐', 'color': '#059669'},
            'bookmarks': {'name': 'Browser Bookmarks', 'icon': '🔖', 'color': '#dc2626'},
            'system_logs': {'name': 'System Logs', 'icon': '📊', 'color': '#7c3aed'},
            'application_logs': {'name': 'Application Logs', 'icon': '🔧', 'color': '#ea580c'},
            'error_logs': {'name': 'Error Logs', 'icon': '⚠️', 'color': '#dc2626'}
        }

    def get_timeline_data(self, start_time=None, end_time=None, sources=None):
        """Get correlated timeline data across all sources"""
        if not start_time:
            start_time = datetime.now() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.now()

        timeline_data = []

        # Clipboard data
        if not sources or 'clipboard' in sources:
            clipboard_data = self._get_clipboard_timeline(start_time, end_time)
            timeline_data.extend(clipboard_data)

        # Browser history
        if not sources or 'browser' in sources:
            browser_data = self._get_browser_timeline(start_time, end_time)
            timeline_data.extend(browser_data)

        # System logs
        if not sources or 'system_logs' in sources:
            system_data = self._get_system_logs_timeline(start_time, end_time)
            timeline_data.extend(system_data)

        # Sort by timestamp
        timeline_data.sort(key=lambda x: x['timestamp'])

        return timeline_data

    def _get_clipboard_timeline(self, start_time, end_time):
        """Get clipboard entries within time range"""
        try:
            conn = sqlite3.connect(str(self.clipboard_db))
            conn.row_factory = sqlite3.Row

            cursor = conn.execute('''
                SELECT id, content, timestamp, content_hash,
                       length(content) as size
                FROM clipboard_history
                WHERE datetime(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time.isoformat(), end_time.isoformat()))

            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry['source'] = 'clipboard'
                entry['type'] = self._classify_content(entry['content'])
                entry['preview'] = self._generate_preview(entry['content'], entry['type'])
                entries.append(entry)

            conn.close()
            return entries
        except Exception as e:
            print(f"Error getting clipboard timeline: {e}")
            return []

    def _get_browser_timeline(self, start_time, end_time):
        """Get browser history within time range"""
        entries = []

        # Firefox history
        firefox_profiles = glob.glob(str(Path.home() / '.mozilla/firefox/*/places.sqlite'))
        for profile_db in firefox_profiles:
            try:
                conn = sqlite3.connect(profile_db)
                conn.row_factory = sqlite3.Row

                # Convert to microseconds for Firefox timestamp
                start_micro = int(start_time.timestamp() * 1000000)
                end_micro = int(end_time.timestamp() * 1000000)

                cursor = conn.execute('''
                    SELECT url, title, last_visit_date, visit_count
                    FROM moz_places
                    WHERE last_visit_date BETWEEN ? AND ?
                    ORDER BY last_visit_date DESC
                    LIMIT 100
                ''', (start_micro, end_micro))

                for row in cursor.fetchall():
                    entry = {
                        'source': 'browser',
                        'type': 'url',
                        'content': row['url'],
                        'title': row['title'],
                        'timestamp': datetime.fromtimestamp(row['last_visit_date'] / 1000000).isoformat(),
                        'visit_count': row['visit_count'],
                        'preview': row['title'] or row['url']
                    }
                    entries.append(entry)

                conn.close()
            except Exception as e:
                print(f"Error reading Firefox history: {e}")

        return entries

    def _get_system_logs_timeline(self, start_time, end_time):
        """Get system logs within time range"""
        entries = []

        try:
            # Use journalctl to get system logs
            cmd = [
                'journalctl',
                '--since', start_time.strftime('%Y-%m-%d %H:%M:%S'),
                '--until', end_time.strftime('%Y-%m-%d %H:%M:%S'),
                '--output=json',
                '--lines=100'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            log_entry = json.loads(line)
                            entry = {
                                'source': 'system_logs',
                                'type': 'log',
                                'content': log_entry.get('MESSAGE', ''),
                                'timestamp': datetime.fromtimestamp(int(log_entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000).isoformat(),
                                'unit': log_entry.get('_SYSTEMD_UNIT', 'unknown'),
                                'priority': log_entry.get('PRIORITY', '6'),
                                'preview': log_entry.get('MESSAGE', '')[:100]
                            }
                            entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error getting system logs: {e}")

        return entries

    def _classify_content(self, content):
        """Classify content type for better visualization"""
        if content.startswith(('http://', 'https://')):
            return 'url'
        elif '@' in content and '.' in content:
            return 'email'
        elif content.isdigit():
            return 'number'
        elif len(content) > 500:
            return 'large_text'
        elif any(keyword in content.lower() for keyword in ['error', 'exception', 'failed', 'warning']):
            return 'error'
        else:
            return 'text'

    def _generate_preview(self, content, content_type):
        """Generate smart preview based on content type"""
        if content_type == 'url':
            return content
        elif content_type == 'large_text':
            return content[:100] + '...' if len(content) > 100 else content
        else:
            return content[:80] + '...' if len(content) > 80 else content

    def get_correlation_analysis(self, timeframe_hours=24):
        """Analyze correlations between different data sources"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=timeframe_hours)

        timeline_data = self.get_timeline_data(start_time, end_time)

        # Group by time windows (15-minute intervals)
        time_windows = {}
        for entry in timeline_data:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                window_key = timestamp.replace(minute=(timestamp.minute // 15) * 15, second=0, microsecond=0)

                if window_key not in time_windows:
                    time_windows[window_key] = {'clipboard': 0, 'browser': 0, 'system_logs': 0}

                time_windows[window_key][entry['source']] += 1
            except:
                continue

        # Convert to correlation data
        correlation_data = []
        for window_time, counts in sorted(time_windows.items()):
            correlation_data.append({
                'timestamp': window_time.isoformat(),
                'clipboard_activity': counts['clipboard'],
                'browser_activity': counts['browser'],
                'system_activity': counts['system_logs'],
                'total_activity': sum(counts.values())
            })

        return correlation_data

    def search_across_sources(self, query, sources=None, limit=50):
        """Search across all data sources"""
        results = []

        if not sources or 'clipboard' in sources:
            clipboard_results = self._search_clipboard(query, limit)
            results.extend(clipboard_results)

        if not sources or 'browser' in sources:
            browser_results = self._search_browser(query, limit)
            results.extend(browser_results)

        # Sort by relevance and timestamp
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return results[:limit]

    def _search_clipboard(self, query, limit):
        """Search clipboard history"""
        try:
            conn = sqlite3.connect(str(self.clipboard_db))
            conn.row_factory = sqlite3.Row

            cursor = conn.execute('''
                SELECT id, content, timestamp, content_hash,
                       length(content) as size
                FROM clipboard_history
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', limit))

            results = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry['source'] = 'clipboard'
                entry['type'] = self._classify_content(entry['content'])
                entry['preview'] = self._generate_preview(entry['content'], entry['type'])
                entry['relevance'] = self._calculate_relevance(entry['content'], query)
                results.append(entry)

            conn.close()
            return results
        except Exception as e:
            print(f"Error searching clipboard: {e}")
            return []

    def _search_browser(self, query, limit):
        """Search browser history"""
        results = []

        firefox_profiles = glob.glob(str(Path.home() / '.mozilla/firefox/*/places.sqlite'))
        for profile_db in firefox_profiles:
            try:
                conn = sqlite3.connect(profile_db)
                conn.row_factory = sqlite3.Row

                cursor = conn.execute('''
                    SELECT url, title, last_visit_date, visit_count
                    FROM moz_places
                    WHERE url LIKE ? OR title LIKE ?
                    ORDER BY last_visit_date DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))

                for row in cursor.fetchall():
                    entry = {
                        'source': 'browser',
                        'type': 'url',
                        'content': row['url'],
                        'title': row['title'],
                        'timestamp': datetime.fromtimestamp(row['last_visit_date'] / 1000000).isoformat() if row['last_visit_date'] else '',
                        'visit_count': row['visit_count'],
                        'preview': row['title'] or row['url'],
                        'relevance': self._calculate_relevance(f"{row['title']} {row['url']}", query)
                    }
                    results.append(entry)

                conn.close()
            except Exception as e:
                print(f"Error searching Firefox history: {e}")

        return results

    def _calculate_relevance(self, content, query):
        """Calculate search relevance score"""
        if not content or not query:
            return 0

        content_lower = content.lower()
        query_lower = query.lower()

        # Exact match gets highest score
        if query_lower in content_lower:
            return 100

        # Word matches
        query_words = query_lower.split()
        content_words = content_lower.split()

        matches = sum(1 for word in query_words if word in content_words)
        return (matches / len(query_words)) * 80 if query_words else 0

    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        try:
            # Clipboard stats
            conn = sqlite3.connect(str(self.clipboard_db))
            cursor = conn.execute('SELECT COUNT(*) FROM clipboard_history')
            clipboard_total = cursor.fetchone()[0]

            cursor = conn.execute('''
                SELECT COUNT(*) FROM clipboard_history
                WHERE datetime(timestamp) > datetime('now', '-24 hours')
            ''')
            clipboard_recent = cursor.fetchone()[0]

            cursor = conn.execute('''
                SELECT COUNT(*) FROM clipboard_history
                WHERE datetime(timestamp) > datetime('now', '-1 hour')
            ''')
            clipboard_hourly = cursor.fetchone()[0]

            conn.close()

            # Database size
            db_size = self.clipboard_db.stat().st_size / (1024 * 1024)  # MB

            return {
                'clipboard': {
                    'total': clipboard_total,
                    'recent_24h': clipboard_recent,
                    'recent_1h': clipboard_hourly,
                    'db_size_mb': round(db_size, 2)
                },
                'system': {
                    'uptime': self._get_system_uptime(),
                    'load_avg': self._get_load_average(),
                    'memory_usage': self._get_memory_usage()
                },
                'data_sources': len(self.data_sources),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'clipboard': {'total': 0, 'recent_24h': 0, 'recent_1h': 0, 'db_size_mb': 0},
                'system': {'uptime': 'Unknown', 'load_avg': 0, 'memory_usage': 0},
                'data_sources': 0,
                'last_updated': datetime.now().isoformat()
            }

    def _get_system_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_hours = uptime_seconds / 3600
                return f"{uptime_hours:.1f}h"
        except:
            return "Unknown"

    def _get_load_average(self):
        """Get system load average"""
        try:
            return os.getloadavg()[0]
        except:
            return 0

    def _get_memory_usage(self):
        """Get memory usage percentage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                mem_total = int([line for line in lines if 'MemTotal' in line][0].split()[1])
                mem_available = int([line for line in lines if 'MemAvailable' in line][0].split()[1])
                return round((1 - mem_available / mem_total) * 100, 1)
        except:
            return 0

observatory = DataObservatory()

@app.route('/')
def main_dashboard():
    """Professional data observatory dashboard"""
    return render_template_string(PROFESSIONAL_TEMPLATE)

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    return jsonify(observatory.get_dashboard_stats())

@app.route('/api/timeline')
def api_timeline():
    """Get timeline data for correlation analysis"""
    hours = request.args.get('hours', 24, type=int)
    sources = request.args.getlist('sources')

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)

    timeline_data = observatory.get_timeline_data(start_time, end_time, sources if sources else None)
    return jsonify(timeline_data)

@app.route('/api/correlation')
def api_correlation():
    """Get correlation analysis data"""
    hours = request.args.get('hours', 24, type=int)
    correlation_data = observatory.get_correlation_analysis(hours)
    return jsonify(correlation_data)

@app.route('/api/search')
def api_search():
    """Universal search across all data sources"""
    query = request.args.get('q', '')
    sources = request.args.getlist('sources')
    limit = request.args.get('limit', 50, type=int)

    if not query:
        return jsonify([])

    results = observatory.search_across_sources(query, sources if sources else None, limit)
    return jsonify(results)

@app.route('/api/data-sources')
def api_data_sources():
    """Get available data sources"""
    return jsonify(observatory.data_sources)

# Professional HTML Template
PROFESSIONAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Data Observatory - Professional Analytics Platform</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Professional Enterprise CSS - Inspired by Grafana/Kibana */
        :root {
            --primary-bg: #0f1419;
            --secondary-bg: #1f2937;
            --surface-bg: #374151;
            --accent-bg: #4f46e5;
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --text-muted: #9ca3af;
            --border-color: #4b5563;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --info-color: #3b82f6;
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            background: var(--primary-bg);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* Professional Header */
        .header {
            background: var(--secondary-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 600;
        }

        .logo-icon {
            font-size: 1.5rem;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .time-range-selector {
            background: var(--surface-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            color: var(--text-primary);
            font-size: 0.875rem;
        }

        .refresh-btn {
            background: var(--accent-bg);
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            color: white;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }

        .refresh-btn:hover {
            background: #4338ca;
            transform: translateY(-1px);
        }

        /* Main Layout */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            gap: 2rem;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--accent-bg);
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-bg), var(--info-color));
        }

        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .stat-title {
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .stat-icon {
            font-size: 1.5rem;
            opacity: 0.8;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .stat-change {
            font-size: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .stat-change.positive {
            color: var(--success-color);
        }

        .stat-change.negative {
            color: var(--error-color);
        }

        /* Search Section */
        .search-section {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .search-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .search-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .data-source-filters {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .filter-chip {
            background: var(--surface-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 0.375rem 0.75rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }

        .filter-chip.active {
            background: var(--accent-bg);
            border-color: var(--accent-bg);
            color: white;
        }

        .filter-chip:hover {
            border-color: var(--accent-bg);
        }

        .search-input-container {
            position: relative;
            margin-bottom: 1rem;
        }

        .search-input {
            width: 100%;
            background: var(--surface-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem 1rem 0.75rem 2.5rem;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.2s;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--accent-bg);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 1.125rem;
        }

        /* Timeline Section */
        .timeline-section {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .chart-container {
            height: 400px;
            position: relative;
        }

        /* Results Section */
        .results-section {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
        }

        .result-item {
            background: var(--surface-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: all 0.2s;
            cursor: pointer;
        }

        .result-item:hover {
            border-color: var(--accent-bg);
            transform: translateX(4px);
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .result-source {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .result-timestamp {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .result-content {
            color: var(--text-primary);
            font-size: 0.875rem;
            line-height: 1.5;
        }

        /* Loading States */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            color: var(--text-muted);
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--border-color);
            border-top: 2px solid var(--accent-bg);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 0.75rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 1rem;
            }

            .header-content {
                flex-direction: column;
                gap: 1rem;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .search-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }
        }

        /* Professional Animations */
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .slide-in {
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <!-- Professional Header -->
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-icon">🏢</span>
                <span>Data Observatory</span>
                <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 400;">Professional Analytics</span>
            </div>
            <div class="header-actions">
                <select class="time-range-selector" id="timeRange">
                    <option value="1">Last Hour</option>
                    <option value="6">Last 6 Hours</option>
                    <option value="24" selected>Last 24 Hours</option>
                    <option value="168">Last Week</option>
                </select>
                <button class="refresh-btn" onclick="refreshDashboard()">
                    🔄 Refresh
                </button>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <div class="main-container">
        <!-- Stats Grid -->
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be populated by JavaScript -->
        </div>

        <!-- Search Section -->
        <div class="search-section">
            <div class="search-header">
                <h2 class="search-title">Universal Data Search</h2>
                <div class="data-source-filters" id="sourceFilters">
                    <!-- Filters will be populated by JavaScript -->
                </div>
            </div>
            <div class="search-input-container">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-input" id="searchInput"
                       placeholder="Search across clipboard, browser history, system logs, and more...">
            </div>
        </div>

        <!-- Timeline Correlation -->
        <div class="timeline-section">
            <div class="section-header">
                <h2 class="section-title">Data Correlation Timeline</h2>
                <div style="font-size: 0.875rem; color: var(--text-muted);">
                    Activity patterns across data sources
                </div>
            </div>
            <div class="chart-container">
                <canvas id="timelineChart"></canvas>
            </div>
        </div>

        <!-- Search Results -->
        <div class="results-section">
            <div class="section-header">
                <h2 class="section-title">Search Results</h2>
                <div id="resultsCount" style="font-size: 0.875rem; color: var(--text-muted);">
                    Ready to search
                </div>
            </div>
            <div id="searchResults">
                <div class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <span>Searching across data sources...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Professional Data Observatory JavaScript
        // Inspired by Grafana and Kibana UX patterns

        class DataObservatory {
            constructor() {
                this.timelineChart = null;
                this.currentTimeRange = 24;
                this.activeFilters = [];
                this.searchTimeout = null;
                this.dataSources = {};

                this.init();
            }

            async init() {
                await this.loadDataSources();
                await this.loadDashboardStats();
                this.setupEventListeners();
                this.initializeCharts();
                this.setupSearch();
            }

            async loadDataSources() {
                try {
                    const response = await fetch('/api/data-sources');
                    this.dataSources = await response.json();
                    this.renderSourceFilters();
                } catch (error) {
                    console.error('Error loading data sources:', error);
                }
            }

            renderSourceFilters() {
                const container = document.getElementById('sourceFilters');
                container.innerHTML = '';

                // Add "All" filter
                const allFilter = this.createFilterChip('all', 'All Sources', '🔍', true);
                container.appendChild(allFilter);

                // Add individual source filters
                Object.entries(this.dataSources).forEach(([key, source]) => {
                    const chip = this.createFilterChip(key, source.name, source.icon, false);
                    container.appendChild(chip);
                });
            }

            createFilterChip(key, name, icon, active = false) {
                const chip = document.createElement('div');
                chip.className = `filter-chip ${active ? 'active' : ''}`;
                chip.innerHTML = `<span>${icon}</span><span>${name}</span>`;
                chip.onclick = () => this.toggleFilter(key, chip);
                return chip;
            }

            toggleFilter(key, chipElement) {
                if (key === 'all') {
                    // Clear all filters and activate "All"
                    this.activeFilters = [];
                    document.querySelectorAll('.filter-chip').forEach(chip => {
                        chip.classList.remove('active');
                    });
                    chipElement.classList.add('active');
                } else {
                    // Toggle individual filter
                    const allChip = document.querySelector('.filter-chip');
                    allChip.classList.remove('active');

                    chipElement.classList.toggle('active');

                    if (chipElement.classList.contains('active')) {
                        if (!this.activeFilters.includes(key)) {
                            this.activeFilters.push(key);
                        }
                    } else {
                        this.activeFilters = this.activeFilters.filter(f => f !== key);
                    }

                    // If no filters active, activate "All"
                    if (this.activeFilters.length === 0) {
                        allChip.classList.add('active');
                    }
                }

                // Trigger search if there's a query
                const searchInput = document.getElementById('searchInput');
                if (searchInput.value.trim()) {
                    this.performSearch(searchInput.value.trim());
                }
            }

            async loadDashboardStats() {
                try {
                    const response = await fetch('/api/dashboard/stats');
                    const stats = await response.json();
                    this.renderStats(stats);
                } catch (error) {
                    console.error('Error loading dashboard stats:', error);
                }
            }

            renderStats(stats) {
                const container = document.getElementById('statsGrid');
                container.innerHTML = '';

                // Clipboard stats
                const clipboardCard = this.createStatCard(
                    'Clipboard Entries',
                    stats.clipboard.total.toLocaleString(),
                    '📋',
                    `+${stats.clipboard.recent_24h} in 24h`,
                    'positive'
                );
                container.appendChild(clipboardCard);

                // Recent activity
                const activityCard = this.createStatCard(
                    'Recent Activity',
                    stats.clipboard.recent_1h.toString(),
                    '⚡',
                    'Last hour',
                    'neutral'
                );
                container.appendChild(activityCard);

                // Database size
                const sizeCard = this.createStatCard(
                    'Database Size',
                    `${stats.clipboard.db_size_mb} MB`,
                    '💾',
                    'Total storage',
                    'neutral'
                );
                container.appendChild(sizeCard);

                // System load
                const loadCard = this.createStatCard(
                    'System Load',
                    stats.system.load_avg.toFixed(2),
                    '📊',
                    `${stats.system.memory_usage}% memory`,
                    stats.system.load_avg > 2 ? 'negative' : 'positive'
                );
                container.appendChild(loadCard);

                // Data sources
                const sourcesCard = this.createStatCard(
                    'Data Sources',
                    stats.data_sources.toString(),
                    '🔗',
                    'Connected',
                    'positive'
                );
                container.appendChild(sourcesCard);

                // Uptime
                const uptimeCard = this.createStatCard(
                    'System Uptime',
                    stats.system.uptime,
                    '🕐',
                    'Running',
                    'positive'
                );
                container.appendChild(uptimeCard);
            }

            createStatCard(title, value, icon, change, changeType) {
                const card = document.createElement('div');
                card.className = 'stat-card fade-in';
                card.innerHTML = `
                    <div class="stat-header">
                        <div class="stat-title">${title}</div>
                        <div class="stat-icon">${icon}</div>
                    </div>
                    <div class="stat-value">${value}</div>
                    <div class="stat-change ${changeType}">
                        ${changeType === 'positive' ? '↗' : changeType === 'negative' ? '↘' : '→'} ${change}
                    </div>
                `;
                return card;
            }

            setupEventListeners() {
                // Time range selector
                document.getElementById('timeRange').addEventListener('change', (e) => {
                    this.currentTimeRange = parseInt(e.target.value);
                    this.refreshTimeline();
                });

                // Search input
                document.getElementById('searchInput').addEventListener('input', (e) => {
                    this.handleSearchInput(e.target.value);
                });

                // Enter key for search
                document.getElementById('searchInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.performSearch(e.target.value.trim());
                    }
                });
            }

            handleSearchInput(query) {
                // Clear previous timeout
                if (this.searchTimeout) {
                    clearTimeout(this.searchTimeout);
                }

                // Debounce search
                this.searchTimeout = setTimeout(() => {
                    if (query.trim().length > 0) {
                        this.performSearch(query.trim());
                    } else {
                        this.clearSearchResults();
                    }
                }, 300);
            }

            async performSearch(query) {
                const resultsContainer = document.getElementById('searchResults');
                const loadingElement = resultsContainer.querySelector('.loading');
                const countElement = document.getElementById('resultsCount');

                // Show loading
                resultsContainer.innerHTML = '';
                loadingElement.style.display = 'flex';
                resultsContainer.appendChild(loadingElement);

                try {
                    const sources = this.activeFilters.length > 0 ? this.activeFilters : [];
                    const params = new URLSearchParams({
                        q: query,
                        limit: 50
                    });

                    sources.forEach(source => params.append('sources', source));

                    const response = await fetch(`/api/search?${params}`);
                    const results = await response.json();

                    this.renderSearchResults(results);
                    countElement.textContent = `${results.length} results found`;

                } catch (error) {
                    console.error('Search error:', error);
                    resultsContainer.innerHTML = '<div class="loading">Search failed. Please try again.</div>';
                }
            }

            renderSearchResults(results) {
                const container = document.getElementById('searchResults');
                container.innerHTML = '';

                if (results.length === 0) {
                    container.innerHTML = '<div class="loading">No results found</div>';
                    return;
                }

                results.forEach((result, index) => {
                    const resultElement = this.createResultItem(result);
                    resultElement.style.animationDelay = `${index * 50}ms`;
                    container.appendChild(resultElement);
                });
            }

            createResultItem(result) {
                const item = document.createElement('div');
                item.className = 'result-item slide-in';

                const sourceInfo = this.dataSources[result.source] || {
                    name: result.source,
                    icon: '📄',
                    color: '#6b7280'
                };

                const timestamp = result.timestamp ?
                    new Date(result.timestamp).toLocaleString() :
                    'Unknown time';

                item.innerHTML = `
                    <div class="result-header">
                        <div class="result-source">
                            <span>${sourceInfo.icon}</span>
                            <span>${sourceInfo.name}</span>
                            ${result.type ? `<span>• ${result.type}</span>` : ''}
                        </div>
                        <div class="result-timestamp">${timestamp}</div>
                    </div>
                    <div class="result-content">${this.escapeHtml(result.preview || result.content)}</div>
                `;

                item.onclick = () => this.showResultDetails(result);

                return item;
            }

            showResultDetails(result) {
                // Create modal or detailed view
                alert(`Full content:\\n\\n${result.content}`);

                // Copy to clipboard
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(result.content);
                }
            }

            clearSearchResults() {
                document.getElementById('searchResults').innerHTML = '';
                document.getElementById('resultsCount').textContent = 'Ready to search';
            }

            async initializeCharts() {
                await this.loadTimelineData();
            }

            async loadTimelineData() {
                try {
                    const response = await fetch(`/api/correlation?hours=${this.currentTimeRange}`);
                    const data = await response.json();
                    this.renderTimelineChart(data);
                } catch (error) {
                    console.error('Error loading timeline data:', error);
                }
            }

            renderTimelineChart(data) {
                const ctx = document.getElementById('timelineChart').getContext('2d');

                if (this.timelineChart) {
                    this.timelineChart.destroy();
                }

                this.timelineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.map(d => new Date(d.timestamp).toLocaleTimeString()),
                        datasets: [
                            {
                                label: 'Clipboard Activity',
                                data: data.map(d => d.clipboard_activity),
                                borderColor: '#6366f1',
                                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                tension: 0.4,
                                fill: true
                            },
                            {
                                label: 'Browser Activity',
                                data: data.map(d => d.browser_activity),
                                borderColor: '#059669',
                                backgroundColor: 'rgba(5, 150, 105, 0.1)',
                                tension: 0.4,
                                fill: true
                            },
                            {
                                label: 'System Activity',
                                data: data.map(d => d.system_activity),
                                borderColor: '#dc2626',
                                backgroundColor: 'rgba(220, 38, 38, 0.1)',
                                tension: 0.4,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#d1d5db'
                                }
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    color: '#9ca3af'
                                },
                                grid: {
                                    color: '#4b5563'
                                }
                            },
                            y: {
                                ticks: {
                                    color: '#9ca3af'
                                },
                                grid: {
                                    color: '#4b5563'
                                }
                            }
                        }
                    }
                });
            }

            async refreshTimeline() {
                await this.loadTimelineData();
            }

            setupSearch() {
                // Focus search on Ctrl+K
                document.addEventListener('keydown', (e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                        e.preventDefault();
                        document.getElementById('searchInput').focus();
                    }
                });
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        // Global functions
        async function refreshDashboard() {
            const observatory = window.dataObservatory;
            if (observatory) {
                await observatory.loadDashboardStats();
                await observatory.refreshTimeline();
            }
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            window.dataObservatory = new DataObservatory();
        });
    </script>
</body>
</html>
'''

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1)
    webbrowser.open('http://localhost:6000')

if __name__ == '__main__':
    print("🏢 Starting Professional Data Observatory...")
    print("=" * 80)
    print("🌟 ENTERPRISE-GRADE DATA CORRELATION PLATFORM")
    print("📊 Inspired by Grafana, Kibana, and Splunk UX patterns")
    print("")
    print("🔗 PROFESSIONAL FEATURES:")
    print("• Timeline correlation across multiple data sources")
    print("• Advanced search and filtering capabilities")
    print("• Real-time system monitoring integration")
    print("• Professional dashboard design patterns")
    print("• Data relationship visualization")
    print("• Contextual data analysis")
    print("")
    print("📱 ACCESS: http://localhost:6000")
    print("=" * 80)

    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host='0.0.0.0', port=6000, debug=False)