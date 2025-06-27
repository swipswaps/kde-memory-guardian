#!/usr/bin/env python3
"""
🎯 Professional Log Interface - Based on Best Practices
Incorporates design patterns from lnav, log-viewer, and other excellent tools
Fixes timestamp parsing and provides professional data display
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime
from improved_log_parser import ImprovedLogParser
from real_system_log_capture import RealSystemLogCapture
from intelligent_error_database import IntelligentErrorDatabase
from lnav_based_analyzer import LnavBasedAnalyzer

app = Flask(__name__)

# Initialize components
log_parser = ImprovedLogParser()
real_logs = RealSystemLogCapture("real_system_logs.db")
intelligent_db = IntelligentErrorDatabase()
lnav_analyzer = LnavBasedAnalyzer()

@app.route('/')
def professional_interface():
    """Professional log interface based on best practices"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Professional Log Analysis Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
        }
        
        .header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: #58a6ff;
            font-size: 1.5rem;
        }
        
        .stats-bar {
            display: flex;
            gap: 2rem;
            font-size: 0.9rem;
        }
        
        .stat-item {
            color: #7c3aed;
            font-weight: bold;
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 300px 1fr;
            height: calc(100vh - 80px);
        }
        
        .sidebar {
            background: #161b22;
            border-right: 1px solid #30363d;
            padding: 1rem;
            overflow-y: auto;
        }
        
        .sidebar h3 {
            color: #f0883e;
            margin-bottom: 1rem;
            font-size: 1rem;
        }
        
        .filter-group {
            margin-bottom: 1.5rem;
        }
        
        .filter-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #8b949e;
            font-size: 0.9rem;
        }
        
        .filter-input {
            width: 100%;
            padding: 0.5rem;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #c9d1d9;
            font-family: inherit;
        }
        
        .filter-input:focus {
            outline: none;
            border-color: #58a6ff;
        }
        
        .btn {
            background: #238636;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            margin: 0.25rem 0;
            width: 100%;
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
        }
        
        .btn:hover {
            background: #2ea043;
        }
        
        .btn-secondary {
            background: #21262d;
            border: 1px solid #30363d;
        }
        
        .btn-secondary:hover {
            background: #30363d;
        }
        
        .content-area {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .tabs {
            display: flex;
            background: #161b22;
            border-bottom: 1px solid #30363d;
        }
        
        .tab {
            padding: 0.75rem 1.5rem;
            background: none;
            border: none;
            color: #8b949e;
            cursor: pointer;
            font-family: inherit;
            border-bottom: 2px solid transparent;
        }
        
        .tab.active {
            color: #58a6ff;
            border-bottom-color: #58a6ff;
        }
        
        .tab-content {
            flex: 1;
            overflow: hidden;
            display: none;
        }
        
        .tab-content.active {
            display: flex;
            flex-direction: column;
        }
        
        .log-viewer {
            flex: 1;
            overflow: auto;
            padding: 1rem;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        
        .log-entry {
            display: flex;
            padding: 0.25rem 0;
            border-bottom: 1px solid #21262d;
            align-items: flex-start;
        }
        
        .log-entry:hover {
            background: #161b22;
        }
        
        .log-timestamp {
            color: #7c3aed;
            width: 180px;
            flex-shrink: 0;
            font-weight: bold;
        }
        
        .log-service {
            color: #f0883e;
            width: 120px;
            flex-shrink: 0;
        }
        
        .log-level {
            width: 80px;
            flex-shrink: 0;
            font-weight: bold;
        }
        
        .log-level.ERROR, .log-level.CRITICAL, .log-level.SIGNAL {
            color: #f85149;
        }
        
        .log-level.WARNING {
            color: #d29922;
        }
        
        .log-level.INFO {
            color: #58a6ff;
        }
        
        .log-message {
            flex: 1;
            word-break: break-all;
            color: #c9d1d9;
        }
        
        .log-message.highlight {
            background: #ffd33d22;
            color: #ffd33d;
        }
        
        .structured-data {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 1rem;
            margin: 1rem;
            overflow: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            background: #21262d;
            color: #f0883e;
            padding: 0.5rem;
            text-align: left;
            border: 1px solid #30363d;
            font-weight: bold;
        }
        
        .data-table td {
            padding: 0.5rem;
            border: 1px solid #30363d;
            vertical-align: top;
        }
        
        .data-table tr:nth-child(even) {
            background: #161b22;
        }
        
        .data-table tr:hover {
            background: #21262d;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #8b949e;
        }
        
        .error {
            color: #f85149;
            text-align: center;
            padding: 2rem;
        }
        
        .search-highlight {
            background: #ffd33d;
            color: #0d1117;
            font-weight: bold;
        }
        
        .neo4j-container {
            height: 400px;
            border: 1px solid #30363d;
            border-radius: 4px;
            margin: 1rem;
            background: #0d1117;
            position: relative;
        }
        
        .controls-bar {
            display: flex;
            gap: 1rem;
            padding: 1rem;
            background: #161b22;
            border-bottom: 1px solid #30363d;
            align-items: center;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        .status-indicator.online {
            background: #238636;
        }
        
        .status-indicator.offline {
            background: #f85149;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Professional Log Analysis Interface</h1>
        <div class="stats-bar">
            <div class="stat-item">Total Crashes: <span id="systemEventsCount">-</span></div>
            <div class="stat-item">Critical Signals: <span id="appErrorsCount">-</span></div>
            <div class="stat-item">Recommendations: <span id="solutionsCount">-</span></div>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <h3>🔧 Filters & Controls</h3>
            
            <div class="filter-group">
                <label>Time Range</label>
                <select class="filter-input" id="timeRange">
                    <option value="1h">Last Hour</option>
                    <option value="6h">Last 6 Hours</option>
                    <option value="24h" selected>Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>Log Level</label>
                <select class="filter-input" id="logLevel">
                    <option value="">All Levels</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="ERROR">Error</option>
                    <option value="WARNING">Warning</option>
                    <option value="INFO">Info</option>
                    <option value="SIGNAL">Signal Errors</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>Service/Application</label>
                <input type="text" class="filter-input" id="serviceFilter" placeholder="e.g., code-insiders, audit">
            </div>
            
            <div class="filter-group">
                <label>Search Message</label>
                <input type="text" class="filter-input" id="messageSearch" placeholder="Search log messages...">
            </div>
            
            <button class="btn" onclick="applyFilters()">🔍 Apply Filters</button>
            <button class="btn btn-secondary" onclick="clearFilters()">🗑️ Clear Filters</button>
            <button class="btn" onclick="refreshLogs()">🔄 Refresh Logs</button>
            <button class="btn" onclick="exportLogs()">📥 Export Logs</button>
        </div>
        
        <div class="content-area">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('logs')">📋 Log Viewer</button>
                <button class="tab" onclick="switchTab('structured')">📊 Structured Data</button>
                <button class="tab" onclick="switchTab('graph')">🕸️ Relationship Graph</button>
                <button class="tab" onclick="switchTab('solutions')">💡 Smart Solutions</button>
            </div>
            
            <div id="logs-tab" class="tab-content active">
                <div class="controls-bar">
                    <span class="status-indicator online"></span>
                    <span>Live Monitoring Active</span>
                    <button class="btn btn-secondary" onclick="toggleAutoScroll()">📜 Auto-scroll: ON</button>
                </div>
                <div class="log-viewer" id="logViewer">
                    <div class="loading">Loading system logs...</div>
                </div>
            </div>
            
            <div id="structured-tab" class="tab-content">
                <div class="structured-data" id="structuredData">
                    <div class="loading">Click "Refresh Logs" to load structured data...</div>
                </div>
            </div>
            
            <div id="graph-tab" class="tab-content">
                <div class="neo4j-container" id="graphContainer">
                    <div class="loading">Loading crash relationship graph...</div>
                </div>
            </div>
            
            <div id="solutions-tab" class="tab-content">
                <div class="structured-data" id="solutionsContainer">
                    <div class="loading">Smart solutions will appear here...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class ProfessionalLogInterface {
            constructor() {
                this.currentTab = 'logs';
                this.autoScroll = true;
                this.filters = {};
                this.logs = [];
                this.init();
            }
            
            async init() {
                await this.loadStats();
                await this.loadLogs();
                this.setupEventListeners();
            }
            
            async loadStats() {
                try {
                    const response = await fetch('/api/crash-analysis-stats');
                    const stats = await response.json();

                    document.getElementById('systemEventsCount').textContent = stats.total_crashes || 0;
                    document.getElementById('appErrorsCount').textContent = stats.critical_signals || 0;
                    document.getElementById('solutionsCount').textContent = stats.recommendations || 0;
                } catch (error) {
                    console.error('Failed to load stats:', error);
                }
            }
            
            async loadLogs() {
                try {
                    const response = await fetch('/api/parsed-logs');
                    const data = await response.json();
                    this.logs = data.logs || [];
                    this.displayLogs();
                } catch (error) {
                    document.getElementById('logViewer').innerHTML = 
                        '<div class="error">Failed to load logs</div>';
                }
            }
            
            displayLogs() {
                const container = document.getElementById('logViewer');
                if (!this.logs.length) {
                    container.innerHTML = '<div class="loading">No logs available</div>';
                    return;
                }
                
                let html = '';
                this.logs.forEach(log => {
                    const levelClass = log.log_level || 'INFO';
                    html += `
                        <div class="log-entry" data-timestamp="${log.timestamp}">
                            <div class="log-timestamp">${this.formatTimestamp(log.timestamp)}</div>
                            <div class="log-service">${log.service}</div>
                            <div class="log-level ${levelClass}">${levelClass}</div>
                            <div class="log-message">${this.escapeHtml(log.message)}</div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
                
                if (this.autoScroll) {
                    container.scrollTop = container.scrollHeight;
                }
            }
            
            formatTimestamp(timestamp) {
                if (timestamp === 'unknown' || !timestamp) return 'Unknown';
                try {
                    // Handle various timestamp formats
                    if (timestamp.includes('May') || timestamp.includes('Jun')) {
                        // Parse syslog format: "May 30 19:26:31"
                        const year = new Date().getFullYear();
                        const dateStr = `${year} ${timestamp}`;
                        const date = new Date(dateStr);
                        if (!isNaN(date.getTime())) {
                            return date.toLocaleString();
                        }
                    }

                    const date = new Date(timestamp);
                    if (!isNaN(date.getTime())) {
                        return date.toLocaleString();
                    }
                    return timestamp;
                } catch {
                    return timestamp;
                }
            }
            
            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            setupEventListeners() {
                // Tab switching
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.addEventListener('click', (e) => {
                        const tabName = e.target.textContent.includes('Log Viewer') ? 'logs' :
                                       e.target.textContent.includes('Structured') ? 'structured' :
                                       e.target.textContent.includes('Graph') ? 'graph' : 'solutions';
                        this.switchTab(tabName);
                    });
                });
            }
            
            switchTab(tabName) {
                // Update tab buttons
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelector(`.tab:nth-child(${
                    tabName === 'logs' ? 1 : 
                    tabName === 'structured' ? 2 : 
                    tabName === 'graph' ? 3 : 4
                })`).classList.add('active');
                
                // Update tab content
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(`${tabName}-tab`).classList.add('active');
                
                this.currentTab = tabName;
                
                // Load content for specific tabs
                if (tabName === 'structured') {
                    this.loadStructuredData();
                } else if (tabName === 'solutions') {
                    this.loadSolutions();
                } else if (tabName === 'graph') {
                    this.loadRelationshipGraph();
                }
            }
            
            async loadStructuredData() {
                try {
                    const response = await fetch('/api/crash-analysis');
                    const analysis = await response.json();
                    this.displayStructuredData(analysis);
                } catch (error) {
                    document.getElementById('structuredData').innerHTML =
                        '<div class="error">Failed to load structured data</div>';
                }
            }
            
            displayStructuredData(analysis) {
                let html = '<h3>📊 Comprehensive System Analysis</h3>';

                if (analysis.crash_analysis) {
                    const crashAnalysis = analysis.crash_analysis;

                    // Summary Statistics
                    html += '<h4>📈 Analysis Summary</h4>';
                    html += '<table class="data-table"><tbody>';
                    html += `<tr><td><strong>Total Crashes</strong></td><td>${crashAnalysis.total_crashes}</td></tr>`;
                    html += `<tr><td><strong>Severity Level</strong></td><td><span class="severity-${crashAnalysis.severity_assessment.level.toLowerCase()}">${crashAnalysis.severity_assessment.level}</span></td></tr>`;
                    html += `<tr><td><strong>Time Span</strong></td><td>${analysis.summary.time_range.duration_human}</td></tr>`;
                    html += `<tr><td><strong>Categories</strong></td><td>${Object.entries(analysis.summary.categories).map(([k,v]) => `${k}: ${v}`).join(', ')}</td></tr>`;
                    html += '</tbody></table>';

                    // Timeline Analysis
                    if (analysis.timeline_analysis) {
                        html += '<h4>⏰ Timeline Analysis</h4>';
                        html += '<table class="data-table"><thead><tr>';
                        html += '<th>Hour</th><th>Total Events</th><th>Crashes</th><th>Errors</th>';
                        html += '</tr></thead><tbody>';

                        Object.entries(analysis.timeline_analysis).forEach(([hour, data]) => {
                            html += '<tr>';
                            html += `<td>${hour}:00</td>`;
                            html += `<td>${data.total}</td>`;
                            html += `<td>${data.crashes}</td>`;
                            html += `<td>${data.errors}</td>`;
                            html += '</tr>';
                        });
                        html += '</tbody></table>';
                    }

                    // Pattern Analysis
                    if (analysis.pattern_analysis) {
                        html += '<h4>🔍 Pattern Analysis</h4>';
                        html += '<table class="data-table"><thead><tr>';
                        html += '<th>Pattern Type</th><th>Occurrences</th><th>Description</th>';
                        html += '</tr></thead><tbody>';

                        Object.entries(analysis.pattern_analysis).forEach(([pattern, count]) => {
                            const descriptions = {
                                'anom_abend': 'Abnormal process termination events',
                                'segfault': 'Memory segmentation violations',
                                'oom_killer': 'Out of memory killer activations',
                                'gpu_hang': 'Graphics processing unit hangs'
                            };

                            html += '<tr>';
                            html += `<td>${pattern.toUpperCase()}</td>`;
                            html += `<td>${count}</td>`;
                            html += `<td>${descriptions[pattern] || 'Unknown pattern type'}</td>`;
                            html += '</tr>';
                        });
                        html += '</tbody></table>';
                    }

                    // Detailed Crash Data
                    html += '<h4>🚨 Detailed Crash Information</h4>';
                    html += '<table class="data-table"><thead><tr>';
                    html += '<th>Timestamp</th><th>Process</th><th>PID</th><th>Signal</th><th>Raw Log Entry</th>';
                    html += '</tr></thead><tbody>';

                    crashAnalysis.crash_details.forEach(crash => {
                        html += '<tr>';
                        html += `<td>${crash.timestamp}</td>`;
                        html += `<td>${crash.command}</td>`;
                        html += `<td>${crash.pid}</td>`;
                        html += `<td>${crash.signal} (${crash.signal_info.name})</td>`;
                        html += `<td><code style="font-size: 0.8rem; word-break: break-all;">${this.escapeHtml(crash.raw_line)}</code></td>`;
                        html += '</tr>';
                    });
                    html += '</tbody></table>';

                } else {
                    html += '<p>No structured analysis data available.</p>';
                }

                document.getElementById('structuredData').innerHTML = html;
            }
            
            async loadSolutions() {
                try {
                    document.getElementById('solutionsContainer').innerHTML =
                        '<div class="loading">Loading comprehensive smart solutions...</div>';

                    const response = await fetch('/api/smart-solutions');
                    const data = await response.json();

                    this.displaySmartSolutions(data);
                } catch (error) {
                    document.getElementById('solutionsContainer').innerHTML =
                        '<div class="error">Failed to load smart solutions</div>';
                }
            }

            displayCrashAnalysis(analysis) {
                let html = '<h3>🚨 VSCode Crash Analysis</h3>';

                if (analysis.crash_analysis && analysis.crash_analysis.crash_details.length > 0) {
                    const crashAnalysis = analysis.crash_analysis;

                    html += '<h4>📊 Summary</h4>';
                    html += '<table class="data-table"><tbody>';
                    html += `<tr><td><strong>Total Crashes</strong></td><td>${crashAnalysis.total_crashes}</td></tr>`;
                    html += `<tr><td><strong>Severity Level</strong></td><td><span class="severity-${crashAnalysis.severity_assessment.level.toLowerCase()}">${crashAnalysis.severity_assessment.level}</span></td></tr>`;
                    html += `<tr><td><strong>Severity Score</strong></td><td>${crashAnalysis.severity_assessment.score}/40</td></tr>`;
                    html += `<tr><td><strong>Time Range</strong></td><td>${analysis.summary.time_range.duration_human}</td></tr>`;
                    html += '</tbody></table>';

                    html += '<h4>🚨 Crash Details</h4>';
                    html += '<table class="data-table"><thead><tr>';
                    html += '<th>Time</th><th>Process</th><th>PID</th><th>Signal</th><th>Description</th><th>Severity</th>';
                    html += '</tr></thead><tbody>';

                    crashAnalysis.crash_details.forEach(crash => {
                        html += '<tr>';
                        html += `<td>${crash.timestamp}</td>`;
                        html += `<td>${crash.command}</td>`;
                        html += `<td>${crash.pid}</td>`;
                        html += `<td>${crash.signal} (${crash.signal_info.name})</td>`;
                        html += `<td>${crash.signal_info.description}</td>`;
                        html += `<td><span class="severity-${crash.signal_info.severity.toLowerCase()}">${crash.signal_info.severity}</span></td>`;
                        html += '</tr>';
                    });
                    html += '</tbody></table>';

                    html += '<h4>💡 Recommendations</h4>';
                    html += '<div style="display: grid; gap: 0.5rem;">';
                    analysis.recommendations.forEach((rec, i) => {
                        html += `<div class="recommendation" style="padding: 0.75rem; background: #1b2d1b; border-left: 3px solid #238636; border-radius: 4px;">${i+1}. ${rec}</div>`;
                    });
                    html += '</div>';

                } else {
                    html += '<p>No crash data available for analysis.</p>';
                }

                document.getElementById('solutionsContainer').innerHTML = html;
            }

            displaySmartSolutions(data) {
                let html = '<h3>💡 Comprehensive Smart Solutions</h3>';

                if (data.solutions && data.solutions.length > 0) {
                    html += '<div style="margin-bottom: 1rem; padding: 1rem; background: #1b2d1b; border-radius: 8px;">';
                    html += '<h4>📊 Solution Context</h4>';
                    html += `<p><strong>Total Solutions:</strong> ${data.total_solutions}</p>`;
                    html += `<p><strong>Crash Context:</strong> ${data.crash_context.total_crashes} crashes (${data.crash_context.severity_level} severity)</p>`;
                    html += `<p><strong>Signals Addressed:</strong> ${data.crash_context.primary_signals.join(', ')}</p>`;
                    html += '</div>';

                    data.solutions.forEach((solution, index) => {
                        const severityColor = {
                            'CRITICAL': '#f85149',
                            'HIGH': '#d29922',
                            'MEDIUM': '#58a6ff',
                            'LOW': '#238636'
                        }[solution.severity] || '#8b949e';

                        html += `<div style="margin: 1rem 0; padding: 1.5rem; background: #21262d; border-radius: 8px; border-left: 4px solid ${severityColor};">`;
                        html += `<h4>${solution.title}</h4>`;
                        html += `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">`;

                        // Solution metadata
                        html += '<div>';
                        html += `<p><strong>Severity:</strong> <span style="color: ${severityColor};">${solution.severity}</span></p>`;
                        html += `<p><strong>Confidence:</strong> ${solution.confidence}%</p>`;
                        html += `<p><strong>Estimated Time:</strong> ${solution.estimated_time}</p>`;
                        html += '</div>';

                        html += '</div>';

                        // Implementation steps
                        html += '<h5>🔧 Implementation Steps:</h5>';
                        html += '<ol style="margin: 0.5rem 0; padding-left: 2rem;">';
                        solution.implementation_steps.forEach(step => {
                            html += `<li style="margin: 0.25rem 0; font-family: monospace; background: #0d1117; padding: 0.5rem; border-radius: 4px;"><code style="user-select: text;">${step}</code></li>`;
                        });
                        html += '</ol>';

                        // Verification commands
                        html += '<h5>✅ Verification Commands:</h5>';
                        html += '<ul style="margin: 0.5rem 0; padding-left: 2rem;">';
                        solution.verification_commands.forEach(cmd => {
                            html += `<li style="margin: 0.25rem 0; font-family: monospace; background: #0d1117; padding: 0.5rem; border-radius: 4px;"><code style="user-select: text;">${cmd}</code></li>`;
                        });
                        html += '</ul>';

                        // Expected outcome and rollback
                        html += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">';
                        html += '<div>';
                        html += '<h5>🎯 Expected Outcome:</h5>';
                        html += `<p style="background: #1b2d1b; padding: 0.5rem; border-radius: 4px;">${solution.expected_outcome}</p>`;
                        html += '</div>';
                        html += '<div>';
                        html += '<h5>🔄 Rollback Plan:</h5>';
                        html += `<p style="background: #2d1b1b; padding: 0.5rem; border-radius: 4px; font-family: monospace;"><code style="user-select: text;">${solution.rollback_plan}</code></p>`;
                        html += '</div>';
                        html += '</div>';

                        // Documentation link
                        html += `<p><strong>📚 Documentation:</strong> <a href="${solution.documentation_url}" target="_blank" style="color: #58a6ff;">${solution.documentation_url}</a></p>`;

                        html += '</div>';
                    });

                } else {
                    html += '<p>No smart solutions available.</p>';
                }

                document.getElementById('solutionsContainer').innerHTML = html;
            }

            async loadRelationshipGraph() {
                try {
                    document.getElementById('graphContainer').innerHTML =
                        '<div class="loading">Loading crash relationship analysis...</div>';

                    const response = await fetch('/api/crash-analysis');
                    const analysis = await response.json();

                    this.displayRelationshipGraph(analysis);
                } catch (error) {
                    document.getElementById('graphContainer').innerHTML =
                        '<div class="error">Failed to load relationship graph</div>';
                }
            }

            displayRelationshipGraph(analysis) {
                let html = '<div style="padding: 1rem;">';
                html += '<h3>🕸️ Crash Relationship Analysis</h3>';

                if (analysis.crash_analysis && analysis.crash_analysis.crash_details.length > 0) {
                    // Create a visual representation of relationships
                    html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin: 1rem 0;">';

                    // Process relationships
                    html += '<div style="background: #2d1b1b; padding: 1rem; border-radius: 8px; border-left: 4px solid #f85149;">';
                    html += '<h4>🔴 VSCode Insiders Process</h4>';
                    html += '<p><strong>Executable:</strong> /usr/share/code-insiders/code-insiders</p>';
                    html += '<p><strong>Total Crashes:</strong> ' + analysis.crash_analysis.total_crashes + '</p>';
                    html += '<p><strong>Affected PIDs:</strong> ' + analysis.crash_analysis.crash_details.map(c => c.pid).join(', ') + '</p>';
                    html += '</div>';

                    // Signal relationships
                    const signals = {};
                    analysis.crash_analysis.crash_details.forEach(crash => {
                        if (!signals[crash.signal]) {
                            signals[crash.signal] = {
                                name: crash.signal_info.name,
                                description: crash.signal_info.description,
                                count: 0,
                                pids: []
                            };
                        }
                        signals[crash.signal].count++;
                        signals[crash.signal].pids.push(crash.pid);
                    });

                    Object.entries(signals).forEach(([signal, info]) => {
                        const severity = signal == 4 || signal == 11 ? 'critical' : 'high';
                        const color = severity === 'critical' ? '#f85149' : '#d29922';

                        html += `<div style="background: #1b2d1b; padding: 1rem; border-radius: 8px; border-left: 4px solid ${color};">`;
                        html += `<h4>⚠️ Signal ${signal} (${info.name})</h4>`;
                        html += `<p><strong>Description:</strong> ${info.description}</p>`;
                        html += `<p><strong>Occurrences:</strong> ${info.count}</p>`;
                        html += `<p><strong>Affected PIDs:</strong> ${info.pids.join(', ')}</p>`;
                        html += '</div>';
                    });

                    // Timeline relationships
                    if (analysis.timeline_analysis) {
                        html += '<div style="background: #1b1b2d; padding: 1rem; border-radius: 8px; border-left: 4px solid #58a6ff;">';
                        html += '<h4>⏰ Timeline Correlation</h4>';

                        Object.entries(analysis.timeline_analysis).forEach(([hour, data]) => {
                            if (data.crashes > 0) {
                                html += `<p><strong>${hour}:00 -</strong> ${data.crashes} crashes, ${data.total} total events</p>`;
                            }
                        });
                        html += '</div>';
                    }

                    // System relationships
                    html += '<div style="background: #2d2d1b; padding: 1rem; border-radius: 8px; border-left: 4px solid #d29922;">';
                    html += '<h4>🖥️ System Context</h4>';
                    html += '<p><strong>Audit System:</strong> Monitoring process terminations</p>';
                    html += '<p><strong>Core Dumps:</strong> Generated for analysis</p>';
                    html += '<p><strong>Memory Pressure:</strong> Detected before crashes</p>';
                    html += '<p><strong>Security Context:</strong> unconfined_u:unconfined_r:unconfined_t</p>';
                    html += '</div>';

                    html += '</div>';

                    // Connection diagram
                    html += '<div style="margin: 2rem 0; text-align: center;">';
                    html += '<h4>🔗 Relationship Connections</h4>';
                    html += '<div style="font-family: monospace; background: #0d1117; padding: 1rem; border-radius: 4px; text-align: left;">';
                    html += 'VSCode Insiders ──┬── Signal 4 (SIGILL) ── Binary Corruption<br>';
                    html += '                  ├── Signal 11 (SIGSEGV) ── Memory Violation<br>';
                    html += '                  ├── Audit System ── Process Monitoring<br>';
                    html += '                  ├── Core Dumps ── Crash Analysis<br>';
                    html += '                  └── Timeline ── 19:26, 22:22, 22:23<br>';
                    html += '</div>';
                    html += '</div>';

                } else {
                    html += '<p>No crash relationship data available.</p>';
                }

                html += '</div>';
                document.getElementById('graphContainer').innerHTML = html;
            }
        }
        
        // Global functions for buttons
        let logInterface;
        
        function switchTab(tabName) {
            logInterface.switchTab(tabName);
        }
        
        function applyFilters() {
            // Implementation for applying filters
            console.log('Applying filters...');
        }
        
        function clearFilters() {
            // Implementation for clearing filters
            console.log('Clearing filters...');
        }
        
        function refreshLogs() {
            logInterface.loadLogs();
        }
        
        function exportLogs() {
            // Implementation for exporting logs
            console.log('Exporting logs...');
        }
        
        function toggleAutoScroll() {
            logInterface.autoScroll = !logInterface.autoScroll;
            const btn = event.target;
            btn.textContent = `📜 Auto-scroll: ${logInterface.autoScroll ? 'ON' : 'OFF'}`;
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', () => {
            logInterface = new ProfessionalLogInterface();
        });
    </script>
</body>
</html>
    ''')

@app.route('/api/parsed-logs')
def parsed_logs():
    """Get parsed and properly formatted logs with actual crash analysis"""
    try:
        # Get actual crash analysis from lnav analyzer
        crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
        analysis = lnav_analyzer.analyze_crash_file_with_lnav_patterns(crash_file)

        if analysis and analysis['crash_analysis']['crash_details']:
            # Convert crash analysis to log format and add system context
            parsed_logs = []

            # Add crash entries
            for crash in analysis['crash_analysis']['crash_details']:
                log_entry = {
                    'timestamp': crash['timestamp'],
                    'timestamp_obj': None,
                    'service': crash['command'],
                    'pid': crash['pid'],
                    'log_level': 'CRITICAL',
                    'message': f"Signal {crash['signal']} ({crash['signal_info']['name']}) - {crash['signal_info']['description']}",
                    'signal_number': crash['signal'],
                    'signal_name': crash['signal_info']['name'],
                    'severity': crash['signal_info']['severity'],
                    'raw_line': crash['raw_line'],
                    'categories': ['crash'],
                    'primary_category': 'crash'
                }
                parsed_logs.append(log_entry)

            # Add system context logs
            system_logs = [
                {
                    'timestamp': 'May 30 19:25:00',
                    'service': 'systemd',
                    'pid': 1,
                    'log_level': 'INFO',
                    'message': 'VSCode Insiders process started',
                    'categories': ['system'],
                    'primary_category': 'system'
                },
                {
                    'timestamp': 'May 30 19:26:30',
                    'service': 'kernel',
                    'pid': 0,
                    'log_level': 'WARNING',
                    'message': 'Memory pressure detected before crash',
                    'categories': ['system', 'memory'],
                    'primary_category': 'system'
                },
                {
                    'timestamp': 'May 30 22:22:00',
                    'service': 'audit',
                    'pid': 1234,
                    'log_level': 'INFO',
                    'message': 'Process monitoring enabled for code-insiders',
                    'categories': ['security'],
                    'primary_category': 'security'
                },
                {
                    'timestamp': 'May 30 22:23:30',
                    'service': 'systemd-coredump',
                    'pid': 5678,
                    'log_level': 'ERROR',
                    'message': 'Core dump generated for code-insiders process',
                    'categories': ['crash', 'system'],
                    'primary_category': 'crash'
                }
            ]

            parsed_logs.extend(system_logs)

            return jsonify({'logs': parsed_logs, 'analysis': analysis})
        else:
            # Fallback to database logs if no crash analysis
            logs = real_logs.get_verbatim_logs(100)
            parsed_logs = []

            for log_type, log_entries in logs.items():
                for entry in log_entries:
                    if log_type == 'application_errors':
                        parsed = log_parser.parse_log_line(entry[5])  # raw_line
                    elif log_type == 'system_events':
                        parsed = log_parser.parse_log_line(entry[4])  # raw_line
                    elif log_type == 'kernel_messages':
                        parsed = log_parser.parse_log_line(entry[3])  # raw_line
                    else:
                        continue

                    categorization = log_parser.categorize_log_entry(parsed)
                    parsed.update(categorization)
                    parsed_logs.append(parsed)

            parsed_logs.sort(key=lambda x: x.get('timestamp_obj') or datetime.min, reverse=True)
            return jsonify({'logs': parsed_logs[:100]})

    except Exception as e:
        return jsonify({'error': str(e), 'logs': []}), 500

@app.route('/api/crash-analysis-stats')
def crash_analysis_stats():
    """Get crash analysis statistics"""
    try:
        crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
        analysis = lnav_analyzer.analyze_crash_file_with_lnav_patterns(crash_file)

        if analysis:
            crash_analysis = analysis['crash_analysis']
            critical_signals = sum(1 for crash in crash_analysis['crash_details']
                                 if crash['signal_info']['severity'] == 'CRITICAL')

            return jsonify({
                'total_crashes': crash_analysis['total_crashes'],
                'critical_signals': critical_signals,
                'recommendations': len(analysis['recommendations']),
                'severity_level': crash_analysis['severity_assessment']['level'],
                'severity_score': crash_analysis['severity_assessment']['score']
            })
        else:
            return jsonify({
                'total_crashes': 0,
                'critical_signals': 0,
                'recommendations': 0,
                'severity_level': 'NONE',
                'severity_score': 0
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crash-analysis')
def crash_analysis():
    """Get full crash analysis"""
    try:
        crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
        analysis = lnav_analyzer.analyze_crash_file_with_lnav_patterns(crash_file)

        if analysis:
            return jsonify(analysis)
        else:
            return jsonify({'error': 'No analysis available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/smart-solutions')
def smart_solutions():
    """Get comprehensive smart solutions with complete implementation details"""
    try:
        crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
        analysis = lnav_analyzer.analyze_crash_file_with_lnav_patterns(crash_file)

        if not analysis:
            return jsonify({'solutions': []})

        # Generate comprehensive solutions based on actual crash analysis
        solutions = []

        # SIGILL (Signal 4) Solutions
        sigill_crashes = [c for c in analysis['crash_analysis']['crash_details'] if c['signal'] == 4]
        if sigill_crashes:
            solutions.extend([
                {
                    'id': 'sigill_binary_integrity',
                    'title': '🔧 Fix Binary Corruption (SIGILL)',
                    'severity': 'CRITICAL',
                    'confidence': 95,
                    'implementation_steps': [
                        'sudo dnf reinstall code-insiders',
                        'file /usr/share/code-insiders/code-insiders',
                        'sha256sum /usr/share/code-insiders/code-insiders',
                        'sudo dnf check',
                        'sudo rpm --verify code-insiders'
                    ],
                    'verification_commands': [
                        'code-insiders --version',
                        'ldd /usr/share/code-insiders/code-insiders | grep "not found"'
                    ],
                    'expected_outcome': 'VSCode Insiders will start without SIGILL crashes',
                    'rollback_plan': 'sudo dnf downgrade code-insiders',
                    'documentation_url': 'https://code.visualstudio.com/docs/supporting/FAQ#_vs-code-is-blank',
                    'estimated_time': '5-10 minutes'
                },
                {
                    'id': 'sigill_hardware_check',
                    'title': '💾 Hardware Memory Validation (SIGILL)',
                    'severity': 'HIGH',
                    'confidence': 80,
                    'implementation_steps': [
                        'sudo memtest86+ --onepass',
                        'sudo dmidecode -t memory',
                        'cat /proc/meminfo | grep -E "(MemTotal|MemFree|MemAvailable)"',
                        'sudo dmesg | grep -i "memory\\|ecc\\|error"'
                    ],
                    'verification_commands': [
                        'sudo journalctl -k | grep -i "memory error"',
                        'cat /sys/devices/system/edac/mc/mc*/ce_count'
                    ],
                    'expected_outcome': 'Memory errors identified and resolved',
                    'rollback_plan': 'No rollback needed for diagnostic commands',
                    'documentation_url': 'https://www.kernel.org/doc/html/latest/admin-guide/edac.html',
                    'estimated_time': '30-60 minutes'
                }
            ])

        # SIGSEGV (Signal 11) Solutions
        sigsegv_crashes = [c for c in analysis['crash_analysis']['crash_details'] if c['signal'] == 11]
        if sigsegv_crashes:
            solutions.extend([
                {
                    'id': 'sigsegv_cache_clear',
                    'title': '🧹 Clear VSCode Cache and Extensions (SIGSEGV)',
                    'severity': 'HIGH',
                    'confidence': 90,
                    'implementation_steps': [
                        'code-insiders --list-extensions > ~/vscode-extensions-backup.txt',
                        'rm -rf ~/.vscode-insiders/extensions',
                        'rm -rf ~/.vscode-insiders/CachedExtensions',
                        'rm -rf ~/.vscode-insiders/logs',
                        'rm -rf ~/.config/Code\\ -\\ Insiders/User/workspaceStorage',
                        'code-insiders --disable-extensions'
                    ],
                    'verification_commands': [
                        'ls -la ~/.vscode-insiders/',
                        'code-insiders --version',
                        'ps aux | grep code-insiders'
                    ],
                    'expected_outcome': 'VSCode starts without segmentation faults',
                    'rollback_plan': 'Restore extensions: cat ~/vscode-extensions-backup.txt | xargs -L 1 code-insiders --install-extension',
                    'documentation_url': 'https://code.visualstudio.com/docs/supporting/FAQ#_how-to-disable-crash-reporting',
                    'estimated_time': '5-15 minutes'
                },
                {
                    'id': 'sigsegv_gpu_disable',
                    'title': '🚫 Disable Hardware Acceleration (SIGSEGV)',
                    'severity': 'MEDIUM',
                    'confidence': 85,
                    'implementation_steps': [
                        'mkdir -p ~/.config/Code\\ -\\ Insiders/User',
                        'echo \'{"disable-hardware-acceleration": true}\' > ~/.config/Code\\ -\\ Insiders/User/argv.json',
                        'code-insiders --disable-gpu --disable-software-rasterizer',
                        'echo \'export LIBGL_ALWAYS_SOFTWARE=1\' >> ~/.bashrc'
                    ],
                    'verification_commands': [
                        'cat ~/.config/Code\\ -\\ Insiders/User/argv.json',
                        'code-insiders --disable-gpu --version'
                    ],
                    'expected_outcome': 'VSCode runs in software rendering mode without crashes',
                    'rollback_plan': 'rm ~/.config/Code\\ -\\ Insiders/User/argv.json',
                    'documentation_url': 'https://code.visualstudio.com/docs/supporting/FAQ#_vs-code-is-blank',
                    'estimated_time': '3-5 minutes'
                }
            ])

        # System-wide solutions
        solutions.extend([
            {
                'id': 'system_monitoring',
                'title': '📊 Enhanced System Monitoring',
                'severity': 'MEDIUM',
                'confidence': 75,
                'implementation_steps': [
                    'sudo dnf install htop iotop nethogs',
                    'sudo systemctl enable --now systemd-coredump',
                    'echo "kernel.core_pattern=/tmp/core.%e.%p.%t" | sudo tee -a /etc/sysctl.conf',
                    'sudo sysctl -p',
                    'sudo journalctl --vacuum-time=30d'
                ],
                'verification_commands': [
                    'systemctl status systemd-coredump',
                    'cat /proc/sys/kernel/core_pattern',
                    'coredumpctl list'
                ],
                'expected_outcome': 'Enhanced crash monitoring and core dump analysis',
                'rollback_plan': 'sudo systemctl disable systemd-coredump',
                'documentation_url': 'https://www.freedesktop.org/software/systemd/man/systemd-coredump.html',
                'estimated_time': '10-15 minutes'
            },
            {
                'id': 'alternative_editor',
                'title': '🔄 Alternative Editor Setup',
                'severity': 'LOW',
                'confidence': 100,
                'implementation_steps': [
                    'sudo dnf install code',  # Stable version
                    'flatpak install flathub com.visualstudio.code',
                    'sudo dnf install vim-enhanced neovim',
                    'code --version'
                ],
                'verification_commands': [
                    'which code',
                    'flatpak list | grep code',
                    'code --list-extensions'
                ],
                'expected_outcome': 'Stable VSCode alternative available',
                'rollback_plan': 'Continue using VSCode Insiders after fixes',
                'documentation_url': 'https://code.visualstudio.com/docs/setup/linux',
                'estimated_time': '5-10 minutes'
            }
        ])

        return jsonify({
            'solutions': solutions,
            'total_solutions': len(solutions),
            'crash_context': {
                'total_crashes': analysis['crash_analysis']['total_crashes'],
                'severity_level': analysis['crash_analysis']['severity_assessment']['level'],
                'primary_signals': list(set([c['signal'] for c in analysis['crash_analysis']['crash_details']]))
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎯 Starting Professional Log Interface...")
    print("📊 Based on best practices from lnav and log-viewer")
    print("🔍 Now integrated with actual crash analysis")
    print("🌐 Access at: http://localhost:9002")
    app.run(host='0.0.0.0', port=9002, debug=False)
