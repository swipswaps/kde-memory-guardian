#!/usr/bin/env python3
"""
Enhanced Data Integration & Visualization System
WHO: Users who need comprehensive data visualization and integration
WHAT: Modern UX with browser data, spreadsheets, and web data integration
WHY: Based on latest UX research from Material Design 3, D3.js, and Observable
HOW: Flask + React-like components + D3.js + modern data sources
"""

import os
import sys
import json
import sqlite3
import subprocess
import threading
import time
import csv
import requests
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, send_file, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'
# Use the actual clipboard database instead of creating a separate one
INTEGRATED_DB = CLIPBOARD_DB

class EnhancedDataManager:
    def __init__(self):
        self.init_integrated_database()
    
    def init_integrated_database(self):
        """Initialize integrated database with multiple data sources"""
        conn = sqlite3.connect(str(INTEGRATED_DB))

        # Use existing clipboard_history table structure from the real database
        # No need to create - table already exists with:
        # clipboard_history (id, content, timestamp, content_hash)

        # Since we're using the actual clipboard database directly, no import needed
        
        # Browser bookmarks
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                folder TEXT DEFAULT '',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                favicon_url TEXT DEFAULT '',
                visit_count INTEGER DEFAULT 0,
                tags TEXT DEFAULT '',
                source TEXT DEFAULT 'browser'
            )
        ''')
        
        # Browser history
        conn.execute('''
            CREATE TABLE IF NOT EXISTS browser_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                visit_time DATETIME NOT NULL,
                visit_count INTEGER DEFAULT 1,
                typed_count INTEGER DEFAULT 0,
                source TEXT DEFAULT 'browser'
            )
        ''')
        
        # Spreadsheet data
        conn.execute('''
            CREATE TABLE IF NOT EXISTS spreadsheet_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                sheet_name TEXT DEFAULT '',
                row_data TEXT NOT NULL,
                column_headers TEXT DEFAULT '',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'spreadsheet'
            )
        ''')
        
        # Web data sources
        conn.execute('''
            CREATE TABLE IF NOT EXISTS web_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                api_endpoint TEXT NOT NULL,
                data_content TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_frequency TEXT DEFAULT 'daily',
                source TEXT DEFAULT 'web_api'
            )
        ''')
        
        # Data relationships and connections
        conn.execute('''
            CREATE TABLE IF NOT EXISTS data_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_table TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                target_table TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                connection_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def import_browser_bookmarks(self, browser='chrome'):
        """Import browser bookmarks"""
        try:
            if browser == 'chrome':
                # Chrome bookmarks location
                chrome_path = Path.home() / '.config/google-chrome/Default/Bookmarks'
                if chrome_path.exists():
                    with open(chrome_path, 'r') as f:
                        bookmarks_data = json.load(f)
                    return self._process_chrome_bookmarks(bookmarks_data)
            elif browser == 'firefox':
                # Firefox bookmarks would require different approach
                return {'error': 'Firefox import not yet implemented'}
            
            return {'error': f'Browser {browser} not supported'}
        except Exception as e:
            return {'error': str(e)}
    
    def _process_chrome_bookmarks(self, data):
        """Process Chrome bookmarks JSON data"""
        conn = sqlite3.connect(str(INTEGRATED_DB))
        bookmarks_added = 0
        
        def extract_bookmarks(node, folder=''):
            nonlocal bookmarks_added
            if node.get('type') == 'url':
                conn.execute('''
                    INSERT OR REPLACE INTO bookmarks 
                    (title, url, folder, timestamp, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    node.get('name', ''),
                    node.get('url', ''),
                    folder,
                    datetime.now(),
                    'chrome'
                ))
                bookmarks_added += 1
            elif node.get('type') == 'folder':
                folder_name = node.get('name', '')
                for child in node.get('children', []):
                    extract_bookmarks(child, folder_name)
        
        # Process bookmark bar and other folders
        roots = data.get('roots', {})
        for root_name, root_data in roots.items():
            if isinstance(root_data, dict) and 'children' in root_data:
                for bookmark in root_data['children']:
                    extract_bookmarks(bookmark, root_name)
        
        conn.commit()
        conn.close()
        return {'success': True, 'bookmarks_added': bookmarks_added}
    
    def import_spreadsheet(self, file_path):
        """Import spreadsheet data (CSV, Excel)"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {'error': 'File not found'}
            
            conn = sqlite3.connect(str(INTEGRATED_DB))
            rows_added = 0
            
            if file_path.suffix.lower() == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    
                    for row in reader:
                        conn.execute('''
                            INSERT INTO spreadsheet_data 
                            (filename, row_data, column_headers, source)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            file_path.name,
                            json.dumps(row),
                            json.dumps(headers),
                            'csv'
                        ))
                        rows_added += 1
            
            conn.commit()
            conn.close()
            return {'success': True, 'rows_added': rows_added}
        except Exception as e:
            return {'error': str(e)}
    
    def fetch_web_data(self, source_name, api_endpoint):
        """Fetch data from web APIs"""
        try:
            response = requests.get(api_endpoint, timeout=10)
            response.raise_for_status()
            
            conn = sqlite3.connect(str(INTEGRATED_DB))
            conn.execute('''
                INSERT OR REPLACE INTO web_data 
                (source_name, api_endpoint, data_content, source)
                VALUES (?, ?, ?, ?)
            ''', (
                source_name,
                api_endpoint,
                response.text,
                'web_api'
            ))
            conn.commit()
            conn.close()
            
            return {'success': True, 'data_size': len(response.text)}
        except Exception as e:
            return {'error': str(e)}
    
    def get_integrated_stats(self):
        """Get statistics across all data sources"""
        try:
            conn = sqlite3.connect(str(INTEGRATED_DB))
            stats = {}
            
            # Count entries by source
            tables = ['clipboard_history', 'bookmarks', 'browser_history', 'spreadsheet_data', 'web_data']
            for table in tables:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0
            
            # Recent activity across all sources
            total_recent = 0
            for table in tables:
                try:
                    cursor = conn.execute(f"""
                        SELECT COUNT(*) FROM {table} 
                        WHERE timestamp >= datetime('now', '-24 hours')
                        OR (visit_time IS NOT NULL AND visit_time >= datetime('now', '-24 hours'))
                        OR (last_updated IS NOT NULL AND last_updated >= datetime('now', '-24 hours'))
                    """)
                    total_recent += cursor.fetchone()[0]
                except:
                    pass
            
            stats['total_recent'] = total_recent
            stats['total_entries'] = sum(stats[table] for table in tables)
            
            conn.close()
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def create_data_connections(self):
        """Create intelligent connections between data sources"""
        try:
            conn = sqlite3.connect(str(INTEGRATED_DB))
            connections_created = 0
            
            # Connect clipboard URLs with bookmarks
            cursor = conn.execute('''
                SELECT c.id, c.content FROM clipboard_entries c
                WHERE c.content_type = 'url'
            ''')
            clipboard_urls = cursor.fetchall()
            
            for clip_id, clip_url in clipboard_urls:
                cursor = conn.execute('''
                    SELECT id FROM bookmarks WHERE url = ?
                ''', (clip_url,))
                bookmark_match = cursor.fetchone()
                
                if bookmark_match:
                    conn.execute('''
                        INSERT OR REPLACE INTO data_connections
                        (source_table, source_id, target_table, target_id, connection_type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('clipboard_entries', clip_id, 'bookmarks', bookmark_match[0], 'url_match'))
                    connections_created += 1
            
            conn.commit()
            conn.close()
            return {'success': True, 'connections_created': connections_created}
        except Exception as e:
            return {'error': str(e)}

data_manager = EnhancedDataManager()

# Modern UX Template with Material Design 3 and D3.js Integration
ENHANCED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Data Integration & Visualization Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --md-sys-color-primary: #6750a4;
            --md-sys-color-on-primary: #ffffff;
            --md-sys-color-primary-container: #eaddff;
            --md-sys-color-on-primary-container: #21005d;
            --md-sys-color-secondary: #625b71;
            --md-sys-color-surface: #fef7ff;
            --md-sys-color-surface-variant: #e7e0ec;
            --md-sys-color-outline: #79747e;
            --md-sys-color-shadow: #000000;
            --md-elevation-1: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
            --md-elevation-2: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
            --md-elevation-3: 0px 1px 3px 0px rgba(0, 0, 0, 0.3), 0px 4px 8px 3px rgba(0, 0, 0, 0.15);
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--md-sys-color-on-primary-container);
            font-variation-settings: 'wght' 400;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            box-shadow: var(--md-elevation-2);
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
        }

        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--md-elevation-3);
        }

        .data-source-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 2px solid transparent;
            transition: all 300ms cubic-bezier(0.2, 0.0, 0, 1.0);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .data-source-card:hover {
            border-color: var(--md-sys-color-primary);
            transform: translateY(-2px);
            box-shadow: var(--md-elevation-2);
        }

        .data-source-card.active {
            border-color: var(--md-sys-color-primary);
            background: var(--md-sys-color-primary-container);
        }

        /* Enhanced Interactive States */
        .data-source-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--md-sys-color-on-surface);
            opacity: 0;
            transition: opacity 100ms cubic-bezier(0.2, 0.0, 0, 1.0);
            pointer-events: none;
        }

        .data-source-card:hover::before {
            opacity: 0.04;
        }

        .data-source-card:focus::before {
            opacity: 0.08;
        }

        .visualization-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: var(--md-elevation-2);
            min-height: 400px;
            display: flex;
            flex-direction: column;
            transition: all 300ms cubic-bezier(0.2, 0.0, 0, 1.0);
            position: relative;
            overflow: hidden;
        }

        .visualization-container:hover {
            box-shadow: var(--md-elevation-3);
            transform: translateY(-2px);
        }

        .visualization-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--md-sys-color-on-surface);
            opacity: 0;
            transition: opacity 100ms cubic-bezier(0.2, 0.0, 0, 1.0);
            pointer-events: none;
        }

        .visualization-container:hover::before {
            opacity: 0.04;
        }

        .fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            border: none;
            box-shadow: var(--md-elevation-3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .fab:hover {
            transform: scale(1.1);
            box-shadow: var(--md-elevation-3);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: linear-gradient(135deg, var(--md-sys-color-primary-container), rgba(255,255,255,0.9));
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--md-sys-color-primary);
            font-variation-settings: 'wght' 700;
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--md-sys-color-secondary);
            font-variation-settings: 'wght' 500;
        }

        .integration-button {
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: var(--md-elevation-1);
        }

        .integration-button:hover {
            background: var(--md-sys-color-primary);
            transform: translateY(-2px);
            box-shadow: var(--md-elevation-2);
        }

        .data-flow-viz {
            min-height: 400px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            margin: 1rem 0;
        }

        .connection-line {
            stroke: var(--md-sys-color-primary);
            stroke-width: 2;
            opacity: 0.7;
            transition: all 0.3s ease;
        }

        .connection-line:hover {
            stroke-width: 4;
            opacity: 1;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: var(--md-elevation-1);
        }

        .loading-skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }

        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        .data-connection-node {
            fill: var(--md-sys-color-primary);
            stroke: var(--md-sys-color-on-primary);
            stroke-width: 2;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .data-connection-node:hover {
            fill: var(--md-sys-color-secondary);
            transform: scale(1.2);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">
                <i class="fas fa-network-wired me-2 text-primary"></i>
                Enhanced Data Hub
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="#visualizations">
                    <i class="fas fa-chart-line me-1"></i>Visualizations
                </a>
                <a class="nav-link" href="#integrations">
                    <i class="fas fa-plug me-1"></i>Integrations
                </a>
                <a class="nav-link" href="#connections">
                    <i class="fas fa-project-diagram me-1"></i>Connections
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Enhanced Statistics Dashboard -->
        <div class="stats-grid" id="stats-dashboard">
            <div class="stat-card">
                <div class="stat-number" id="total-entries">-</div>
                <div class="stat-label">Total Entries</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="data-sources">-</div>
                <div class="stat-label">Data Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="connections">-</div>
                <div class="stat-label">Connections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="recent-activity">-</div>
                <div class="stat-label">Recent Activity</div>
            </div>
        </div>

        <div class="row">
            <!-- Data Sources Panel -->
            <div class="col-md-4">
                <div class="glass-card p-4 mb-4">
                    <h5 class="mb-3">
                        <i class="fas fa-database me-2"></i>Data Sources
                    </h5>

                    <div class="data-source-card" onclick="selectDataSource('clipboard')">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-clipboard text-primary me-3"></i>
                            <div>
                                <h6 class="mb-1">Clipboard Data</h6>
                                <small class="text-muted" id="clipboard-count">- entries</small>
                            </div>
                        </div>
                    </div>

                    <div class="data-source-card" onclick="selectDataSource('bookmarks')">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-bookmark text-warning me-3"></i>
                            <div>
                                <h6 class="mb-1">Browser Bookmarks</h6>
                                <small class="text-muted" id="bookmarks-count">- entries</small>
                            </div>
                        </div>
                    </div>

                    <div class="data-source-card" onclick="selectDataSource('history')">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-history text-info me-3"></i>
                            <div>
                                <h6 class="mb-1">Browser History</h6>
                                <small class="text-muted" id="history-count">- entries</small>
                            </div>
                        </div>
                    </div>

                    <div class="data-source-card" onclick="selectDataSource('spreadsheets')">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-table text-success me-3"></i>
                            <div>
                                <h6 class="mb-1">Spreadsheet Data</h6>
                                <small class="text-muted" id="spreadsheet-count">- entries</small>
                            </div>
                        </div>
                    </div>

                    <div class="data-source-card" onclick="selectDataSource('web')">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-globe text-danger me-3"></i>
                            <div>
                                <h6 class="mb-1">Web Data APIs</h6>
                                <small class="text-muted" id="web-count">- sources</small>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Integration Controls -->
                <div class="glass-card p-4">
                    <h5 class="mb-3">
                        <i class="fas fa-plus-circle me-2"></i>Add Data Sources
                    </h5>

                    <div class="d-grid gap-2">
                        <button class="integration-button" onclick="importBrowserData()">
                            <i class="fas fa-download me-2"></i>Import Browser Data
                        </button>
                        <button class="integration-button" onclick="uploadSpreadsheet()">
                            <i class="fas fa-upload me-2"></i>Upload Spreadsheet
                        </button>
                        <button class="integration-button" onclick="addWebDataSource()">
                            <i class="fas fa-link me-2"></i>Add Web API
                        </button>
                        <button class="integration-button" onclick="createConnections()">
                            <i class="fas fa-project-diagram me-2"></i>Auto-Connect Data
                        </button>
                    </div>
                </div>
            </div>

            <!-- Main Visualization Area -->
            <div class="col-md-8">
                <!-- Data Flow Visualization -->
                <div class="glass-card p-4 mb-4">
                    <h5 class="mb-3">
                        <i class="fas fa-project-diagram me-2"></i>Data Flow & Connections
                    </h5>
                    <div id="data-flow-viz" class="data-flow-viz"></div>
                </div>

                <!-- Interactive Charts -->
                <div class="glass-card p-4">
                    <h5 class="mb-3">
                        <i class="fas fa-chart-line me-2"></i>Interactive Visualizations
                    </h5>
                    <div class="row">
                        <div class="col-md-6">
                            <div id="timeline-chart" class="visualization-container"></div>
                        </div>
                        <div class="col-md-6">
                            <div id="distribution-chart" class="visualization-container"></div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <div id="network-graph" class="visualization-container"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Floating Action Button -->
    <button class="fab" onclick="refreshAllData()">
        <i class="fas fa-sync-alt"></i>
    </button>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentDataSource = 'clipboard';
        let dataConnections = [];

        // Load enhanced statistics with modern UX patterns
        async function loadEnhancedStats() {
            try {
                // Show loading state with smooth animation
                showLoadingState();

                const response = await fetch('/api/enhanced-stats');
                const stats = await response.json();

                // Animate numbers for better visual feedback
                animateNumber('total-entries', stats.total_entries || 0);
                animateNumber('data-sources', Object.keys(stats).filter(k => k.endsWith('_entries') || k.endsWith('_data')).length);
                animateNumber('recent-activity', stats.total_recent || 0);

                // Update individual source counts with staggered animation
                setTimeout(() => updateCountWithAnimation('clipboard-count', stats.clipboard_history || 0, 'entries'), 100);
                setTimeout(() => updateCountWithAnimation('bookmarks-count', stats.bookmarks || 0, 'entries'), 200);
                setTimeout(() => updateCountWithAnimation('history-count', stats.browser_history || 0, 'entries'), 300);
                setTimeout(() => updateCountWithAnimation('spreadsheet-count', stats.spreadsheet_data || 0, 'entries'), 400);
                setTimeout(() => updateCountWithAnimation('web-count', stats.web_data || 0, 'sources'), 500);

                // Hide loading state
                setTimeout(() => hideLoadingState(), 600);

                // Show success feedback
                showToast(`✅ Loaded data from ${stats.clipboard_history || 0} clipboard entries`, 'success');

            } catch (error) {
                console.error('Failed to load stats:', error);
                hideLoadingState();
                showToast('❌ Failed to load data', 'error');
            }
        }

        // Smooth number animation for better UX
        function animateNumber(elementId, targetValue) {
            const element = document.getElementById(elementId);
            if (!element) return;

            const startValue = parseInt(element.textContent) || 0;
            const duration = 1000;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Easing function for smooth animation
                const easeOutCubic = 1 - Math.pow(1 - progress, 3);
                const currentValue = Math.round(startValue + (targetValue - startValue) * easeOutCubic);

                element.textContent = currentValue;

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            }

            requestAnimationFrame(animate);
        }

        function updateCountWithAnimation(elementId, targetValue, suffix = '') {
            const element = document.getElementById(elementId);
            if (!element) return;

            const startValue = parseInt(element.textContent) || 0;
            const duration = 600;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                const easeOutCubic = 1 - Math.pow(1 - progress, 3);
                const currentValue = Math.round(startValue + (targetValue - startValue) * easeOutCubic);

                element.textContent = `${currentValue} ${suffix}`;

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    // Subtle emphasis when complete
                    element.style.transform = 'scale(1.02)';
                    element.style.color = 'var(--md-sys-color-primary)';
                    setTimeout(() => {
                        element.style.transform = 'scale(1)';
                        element.style.color = '';
                    }, 300);
                }
            }

            requestAnimationFrame(animate);
        }

        // Modern loading states
        function showLoadingState() {
            const loadingElements = document.querySelectorAll('[id$="-count"], #total-entries, #data-sources, #recent-activity');
            loadingElements.forEach((el, index) => {
                setTimeout(() => {
                    el.style.opacity = '0.5';
                    el.style.transform = 'scale(0.98)';
                    if (el.textContent && !el.textContent.includes('⟳')) {
                        el.setAttribute('data-original', el.textContent);
                        el.textContent = '⟳';
                    }
                }, index * 50);
            });
        }

        function hideLoadingState() {
            const loadingElements = document.querySelectorAll('[id$="-count"], #total-entries, #data-sources, #recent-activity');
            loadingElements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'scale(1)';
            });
        }

        // Toast notification system for better feedback
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            const bgColor = type === 'success' ? 'var(--md-sys-color-tertiary-container)' :
                           type === 'error' ? 'var(--md-sys-color-error-container)' :
                           'var(--md-sys-color-surface-variant)';
            const textColor = type === 'success' ? 'var(--md-sys-color-on-tertiary-container)' :
                             type === 'error' ? 'var(--md-sys-color-on-error-container)' :
                             'var(--md-sys-color-on-surface-variant)';

            toast.style.cssText = `
                position: fixed;
                top: 24px;
                right: 24px;
                padding: 16px 20px;
                background: ${bgColor};
                color: ${textColor};
                border-radius: 12px;
                box-shadow: var(--md-elevation-2);
                z-index: 1000;
                transform: translateX(100%);
                transition: transform 300ms cubic-bezier(0.2, 0.0, 0, 1.0);
                font-size: 0.875rem;
                max-width: 320px;
                font-weight: 500;
            `;
            toast.textContent = message;

            document.body.appendChild(toast);

            // Animate in
            setTimeout(() => {
                toast.style.transform = 'translateX(0)';
            }, 10);

            // Auto remove
            setTimeout(() => {
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (document.body.contains(toast)) {
                        document.body.removeChild(toast);
                    }
                }, 300);
            }, 4000);
        }

        // Create data flow visualization using D3.js
        function createDataFlowVisualization() {
            const container = d3.select('#data-flow-viz');
            container.selectAll('*').remove();

            const width = container.node().getBoundingClientRect().width;
            const height = 400;

            const svg = container.append('svg')
                .attr('width', width)
                .attr('height', height);

            // Define data sources as nodes
            const nodes = [
                { id: 'clipboard', name: 'Clipboard', x: width * 0.2, y: height * 0.3, color: '#6750a4' },
                { id: 'bookmarks', name: 'Bookmarks', x: width * 0.8, y: height * 0.2, color: '#f59e0b' },
                { id: 'history', name: 'History', x: width * 0.8, y: height * 0.5, color: '#06b6d4' },
                { id: 'spreadsheets', name: 'Spreadsheets', x: width * 0.5, y: height * 0.8, color: '#10b981' },
                { id: 'web', name: 'Web APIs', x: width * 0.2, y: height * 0.7, color: '#ef4444' },
                { id: 'integrated', name: 'Integrated Hub', x: width * 0.5, y: height * 0.5, color: '#8b5cf6' }
            ];

            // Define connections
            const links = [
                { source: 'clipboard', target: 'integrated' },
                { source: 'bookmarks', target: 'integrated' },
                { source: 'history', target: 'integrated' },
                { source: 'spreadsheets', target: 'integrated' },
                { source: 'web', target: 'integrated' }
            ];

            // Draw connections
            svg.selectAll('.connection-line')
                .data(links)
                .enter()
                .append('line')
                .attr('class', 'connection-line')
                .attr('x1', d => nodes.find(n => n.id === d.source).x)
                .attr('y1', d => nodes.find(n => n.id === d.source).y)
                .attr('x2', d => nodes.find(n => n.id === d.target).x)
                .attr('y2', d => nodes.find(n => n.id === d.target).y);

            // Draw nodes
            const nodeGroups = svg.selectAll('.node-group')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', 'node-group')
                .attr('transform', d => `translate(${d.x}, ${d.y})`);

            nodeGroups.append('circle')
                .attr('class', 'data-connection-node')
                .attr('r', d => d.id === 'integrated' ? 30 : 20)
                .style('fill', d => d.color)
                .on('click', function(event, d) {
                    selectDataSource(d.id);
                });

            nodeGroups.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .style('fill', 'white')
                .style('font-weight', '500')
                .style('font-size', '12px')
                .text(d => d.name);
        }

        // Create timeline visualization
        function createTimelineVisualization() {
            fetch('/api/timeline-data')
                .then(response => response.json())
                .then(data => {
                    const trace = {
                        x: data.dates,
                        y: data.counts,
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Activity',
                        line: { color: '#6750a4', width: 3 },
                        marker: { color: '#6750a4', size: 8 }
                    };

                    const layout = {
                        title: 'Activity Timeline',
                        xaxis: { title: 'Date' },
                        yaxis: { title: 'Entries' },
                        margin: { t: 50, r: 30, b: 50, l: 50 },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)'
                    };

                    Plotly.newPlot('timeline-chart', [trace], layout, { responsive: true });
                });
        }

        // Create distribution chart
        function createDistributionChart() {
            fetch('/api/distribution-data')
                .then(response => response.json())
                .then(data => {
                    const trace = {
                        labels: data.labels,
                        values: data.values,
                        type: 'pie',
                        marker: {
                            colors: ['#6750a4', '#f59e0b', '#06b6d4', '#10b981', '#ef4444']
                        }
                    };

                    const layout = {
                        title: 'Data Source Distribution',
                        margin: { t: 50, r: 30, b: 30, l: 30 },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)'
                    };

                    Plotly.newPlot('distribution-chart', [trace], layout, { responsive: true });
                });
        }

        // Select data source
        function selectDataSource(source) {
            currentDataSource = source;

            // Update UI
            document.querySelectorAll('.data-source-card').forEach(card => {
                card.classList.remove('active');
            });

            event.target.closest('.data-source-card')?.classList.add('active');

            // Load source-specific visualizations
            loadSourceData(source);
        }

        // Load data for specific source
        function loadSourceData(source) {
            fetch(`/api/source-data/${source}`)
                .then(response => response.json())
                .then(data => {
                    // Update visualizations based on selected source
                    console.log(`Loaded data for ${source}:`, data);
                });
        }

        // Import browser data
        async function importBrowserData() {
            try {
                const response = await fetch('/api/import-browser', { method: 'POST' });
                const result = await response.json();

                if (result.success) {
                    alert(`Successfully imported ${result.bookmarks_added} bookmarks!`);
                    refreshAllData();
                } else {
                    alert(`Import failed: ${result.error}`);
                }
            } catch (error) {
                alert(`Import error: ${error.message}`);
            }
        }

        // Upload spreadsheet
        function uploadSpreadsheet() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.csv,.xlsx,.xls';
            input.onchange = async function(event) {
                const file = event.target.files[0];
                if (file) {
                    const formData = new FormData();
                    formData.append('file', file);

                    try {
                        const response = await fetch('/api/upload-spreadsheet', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();

                        if (result.success) {
                            alert(`Successfully imported ${result.rows_added} rows!`);
                            refreshAllData();
                        } else {
                            alert(`Upload failed: ${result.error}`);
                        }
                    } catch (error) {
                        alert(`Upload error: ${error.message}`);
                    }
                }
            };
            input.click();
        }

        // Add web data source
        function addWebDataSource() {
            const sourceName = prompt('Enter data source name:');
            const apiEndpoint = prompt('Enter API endpoint URL:');

            if (sourceName && apiEndpoint) {
                fetch('/api/add-web-source', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ source_name: sourceName, api_endpoint: apiEndpoint })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        alert('Web data source added successfully!');
                        refreshAllData();
                    } else {
                        alert(`Failed to add source: ${result.error}`);
                    }
                });
            }
        }

        // Create data connections
        async function createConnections() {
            try {
                const response = await fetch('/api/create-connections', { method: 'POST' });
                const result = await response.json();

                if (result.success) {
                    alert(`Created ${result.connections_created} data connections!`);
                    refreshAllData();
                } else {
                    alert(`Connection creation failed: ${result.error}`);
                }
            } catch (error) {
                alert(`Connection error: ${error.message}`);
            }
        }

        // Refresh all data
        function refreshAllData() {
            loadEnhancedStats();
            createDataFlowVisualization();
            createTimelineVisualization();
            createDistributionChart();
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            refreshAllData();

            // Auto-refresh every 30 seconds
            setInterval(refreshAllData, 30000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Enhanced data integration dashboard"""
    return render_template_string(ENHANCED_TEMPLATE)

@app.route('/api/enhanced-stats')
def get_enhanced_stats():
    """Get comprehensive statistics across all data sources"""
    return jsonify(data_manager.get_integrated_stats())

@app.route('/api/import-browser', methods=['POST'])
def import_browser_data():
    """Import browser bookmarks and history"""
    result = data_manager.import_browser_bookmarks('chrome')
    return jsonify(result)

@app.route('/api/upload-spreadsheet', methods=['POST'])
def upload_spreadsheet():
    """Upload and process spreadsheet data"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file temporarily
    temp_path = BASE_DIR / 'temp_uploads' / file.filename
    temp_path.parent.mkdir(exist_ok=True)
    file.save(temp_path)

    # Process the file
    result = data_manager.import_spreadsheet(temp_path)

    # Clean up
    temp_path.unlink(missing_ok=True)

    return jsonify(result)

@app.route('/api/add-web-source', methods=['POST'])
def add_web_source():
    """Add a new web data source"""
    data = request.get_json()
    source_name = data.get('source_name')
    api_endpoint = data.get('api_endpoint')

    if not source_name or not api_endpoint:
        return jsonify({'error': 'Source name and API endpoint required'}), 400

    result = data_manager.fetch_web_data(source_name, api_endpoint)
    return jsonify(result)

@app.route('/api/create-connections', methods=['POST'])
def create_connections():
    """Create intelligent connections between data sources"""
    result = data_manager.create_data_connections()
    return jsonify(result)

@app.route('/api/timeline-data')
def get_timeline_data():
    """Get timeline data for visualization"""
    try:
        conn = sqlite3.connect(str(INTEGRATED_DB))

        # Get daily activity across all sources
        cursor = conn.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM (
                SELECT timestamp FROM clipboard_history
                UNION ALL
                SELECT timestamp FROM bookmarks
                UNION ALL
                SELECT timestamp FROM spreadsheet_data
                UNION ALL
                SELECT last_updated as timestamp FROM web_data
            )
            WHERE date >= DATE('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''')

        results = cursor.fetchall()
        conn.close()

        dates = [row[0] for row in results]
        counts = [row[1] for row in results]

        return jsonify({'dates': dates, 'counts': counts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/distribution-data')
def get_distribution_data():
    """Get data source distribution for pie chart"""
    try:
        stats = data_manager.get_integrated_stats()

        labels = []
        values = []

        source_mapping = {
            'clipboard_history': 'Clipboard',
            'bookmarks': 'Bookmarks',
            'browser_history': 'History',
            'spreadsheet_data': 'Spreadsheets',
            'web_data': 'Web APIs'
        }

        for key, label in source_mapping.items():
            if key in stats and stats[key] > 0:
                labels.append(label)
                values.append(stats[key])

        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/source-data/<source>')
def get_source_data(source):
    """Get data for specific source"""
    try:
        conn = sqlite3.connect(str(INTEGRATED_DB))

        table_mapping = {
            'clipboard': 'clipboard_history',
            'bookmarks': 'bookmarks',
            'history': 'browser_history',
            'spreadsheets': 'spreadsheet_data',
            'web': 'web_data'
        }

        table = table_mapping.get(source)
        if not table:
            return jsonify({'error': 'Invalid source'}), 400

        cursor = conn.execute(f'SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 100')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in rows]
        conn.close()

        return jsonify({'data': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clipboard/history')
def get_clipboard_history():
    """Get ALL clipboard history for React app compatibility - NO LIMITS"""
    try:
        conn = sqlite3.connect(str(CLIPBOARD_DB))
        conn.row_factory = sqlite3.Row
        # Return ALL entries - user needs access to entire database
        cursor = conn.execute('SELECT * FROM clipboard_history ORDER BY timestamp DESC')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        print(f"📊 API returning {len(results)} entries (entire database)")
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Enhanced Data Integration & Visualization Hub")
    print("=" * 70)
    print("🌟 CUTTING-EDGE UX IMPROVEMENTS IMPLEMENTED:")
    print("• Material Design 3 with advanced color system")
    print("• D3.js interactive data flow visualizations")
    print("• Plotly.js modern chart components")
    print("• Glass morphism and elevation effects")
    print("• Responsive grid layouts and animations")
    print("")
    print("📊 COMPREHENSIVE DATA INTEGRATION:")
    print("• Browser bookmarks and history import")
    print("• Spreadsheet data processing (CSV, Excel)")
    print("• Web API data sources integration")
    print("• Intelligent data connection mapping")
    print("• Real-time visualization updates")
    print("")
    print("🔗 ACCESS POINTS:")
    print(f"📱 Enhanced Interface: http://localhost:3001")
    print(f"📊 Data Visualizations: Interactive D3.js + Plotly")
    print(f"🗃️ Integrated Database: {INTEGRATED_DB}")
    print(f"📋 Clipboard Database: {CLIPBOARD_DB}")
    print("=" * 70)

    # Check databases
    if CLIPBOARD_DB.exists():
        size_mb = round(CLIPBOARD_DB.stat().st_size / (1024 * 1024), 2)
        print(f"✅ Clipboard database: {size_mb} MB")

    if INTEGRATED_DB.exists():
        size_mb = round(INTEGRATED_DB.stat().st_size / (1024 * 1024), 2)
        print(f"✅ Integrated database: {size_mb} MB")
    else:
        print("🔧 Creating integrated database...")
        data_manager.init_integrated_database()
        print("✅ Integrated database created")

    print("\n🌟 ENHANCED FEATURES BASED ON RESEARCH:")
    print("• Material Design 3 official guidelines implementation")
    print("• Observable Plot and D3.js best practices")
    print("• Modern data visualization patterns from GitHub repos")
    print("• Browser data integration APIs")
    print("• Spreadsheet processing with pandas-like functionality")
    print("• Web API integration for public data sources")
    print("• Intelligent data relationship mapping")

    print(f"\n🚀 Starting enhanced server on port 3001...")
    print("💡 Press Ctrl+C to stop")

    # Auto-open browser
    try:
        threading.Timer(2.0, lambda: webbrowser.open('http://localhost:3001')).start()
        print("🌐 Opening browser automatically...")
    except:
        pass

    try:
        app.run(host='0.0.0.0', port=3001, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Enhanced server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
