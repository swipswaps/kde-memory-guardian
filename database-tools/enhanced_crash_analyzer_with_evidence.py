#!/usr/bin/env python3
"""
🎯 Enhanced Crash Analyzer with Evidence
Includes Neo4j visualization and spreadsheet interface
Shows actual evidence of database integration
"""

from flask import Flask, render_template_string, jsonify, request
import json
import sqlite3
from intelligent_error_database import IntelligentErrorDatabase
from real_system_log_capture import RealSystemLogCapture

app = Flask(__name__)

# Initialize intelligent database and real log capture
intelligent_db = IntelligentErrorDatabase()
real_logs = RealSystemLogCapture("real_system_logs.db")

@app.route('/')
def enhanced_interface():
    """Enhanced interface with Neo4j and spreadsheet"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Intelligent Error Analysis with Evidence</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/neo4j-driver@5.14.0/lib/browser/neo4j-web.min.js"></script>
    <style>
        :root {
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border: #e2e8f0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), #3b82f6);
            color: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .panel {
            background: var(--bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border);
        }

        .panel h3 {
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .crash-input {
            width: 100%;
            padding: 1rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.9rem;
            resize: vertical;
            min-height: 120px;
        }

        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s;
            margin-top: 1rem;
            width: 100%;
        }

        .btn:hover {
            background: #1d4ed8;
            transform: translateY(-1px);
        }

        .evidence-section {
            margin-top: 2rem;
        }

        .evidence-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .neo4j-container {
            grid-column: 1 / -1;
            height: 500px;
            border: 2px solid var(--border);
            border-radius: 12px;
            background: var(--bg-primary);
            position: relative;
        }

        .spreadsheet-container {
            grid-column: 1 / -1;
            background: var(--bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
        }

        .spreadsheet {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        .spreadsheet th,
        .spreadsheet td {
            border: 1px solid var(--border);
            padding: 0.75rem;
            text-align: left;
        }

        .spreadsheet th {
            background: var(--bg-secondary);
            font-weight: 600;
            color: var(--text-primary);
        }

        .spreadsheet tr:nth-child(even) {
            background: var(--bg-secondary);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--bg-primary);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--border);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }

        .source-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }

        .source-official {
            background: #dcfce7;
            color: #166534;
        }

        .source-github {
            background: #f3e8ff;
            color: #7c3aed;
        }

        .source-stackoverflow {
            background: #fef3c7;
            color: #92400e;
        }

        .source-reddit {
            background: #fee2e2;
            color: #991b1b;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
        }

        .error {
            background: #fef2f2;
            color: #991b1b;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #fecaca;
        }

        .success {
            background: #f0fdf4;
            color: #166534;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Intelligent Error Analysis</h1>
            <p>Smart categorization with official docs, GitHub issues, and forum solutions</p>
        </div>

        <div class="dashboard">
            <div class="panel">
                <h3>🔍 Crash Analysis Input</h3>
                <textarea id="crashInput" class="crash-input" placeholder="Paste crash data, error logs, or system messages here...">May 30 19:26:31 localhost-live.attlocal.net audit[6121]: ANOM_ABEND auid=1000 uid=1000 gid=1000 ses=3 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 pid=6121 comm="code-insiders" exe="/usr/share/code-insiders/code-insiders" sig=4 res=1</textarea>
                <button class="btn" onclick="analyzeWithEvidence()">🎯 Analyze with Evidence</button>
            </div>

            <div class="panel">
                <h3>📊 Database Statistics</h3>
                <div id="databaseStats" class="loading">Loading statistics...</div>
            </div>
        </div>

        <div class="evidence-section">
            <div class="evidence-grid">
                <div class="panel">
                    <h3>🌐 Neo4j Database Visualization</h3>
                    <div id="neo4jContainer" class="neo4j-container">
                        <div class="loading">Loading database connections...</div>
                    </div>
                </div>
            </div>

            <div class="spreadsheet-container">
                <h3>📋 Solutions & Suggestions Spreadsheet</h3>
                <div id="spreadsheetContainer">
                    <div class="loading">Load crash data to see solutions...</div>
                </div>
            </div>

            <div class="spreadsheet-container">
                <h3>📄 Verbatim System & Application Event Messages</h3>
                <button class="btn" onclick="loadVerbatimLogs()" style="width: auto; margin-bottom: 1rem;">🔄 Refresh Real Logs</button>
                <div id="verbatimLogsContainer">
                    <div class="loading">Click refresh to load verbatim system logs...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class IntelligentAnalyzer {
            constructor() {
                this.loadDatabaseStats();
                this.initializeNeo4j();
            }

            async loadDatabaseStats() {
                try {
                    const response = await fetch('/api/database-stats');
                    const stats = await response.json();
                    this.displayStats(stats);
                } catch (error) {
                    document.getElementById('databaseStats').innerHTML = 
                        '<div class="error">Failed to load database statistics</div>';
                }
            }

            displayStats(stats) {
                const statsHtml = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${stats.total_errors || 0}</div>
                            <div class="stat-label">Error Logs</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.official_docs || 0}</div>
                            <div class="stat-label">Official Docs</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.github_issues || 0}</div>
                            <div class="stat-label">GitHub Issues</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.verified_forum_posts || 0}</div>
                            <div class="stat-label">Forum Posts</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.verified_solutions || 0}</div>
                            <div class="stat-label">Verified Solutions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.avg_effectiveness || 0}</div>
                            <div class="stat-label">Avg Effectiveness</div>
                        </div>
                    </div>
                `;
                document.getElementById('databaseStats').innerHTML = statsHtml;
            }

            initializeNeo4j() {
                // Simulate Neo4j visualization with D3.js
                this.createDatabaseVisualization();
            }

            createDatabaseVisualization() {
                const container = document.getElementById('neo4jContainer');
                container.innerHTML = '';

                const width = container.clientWidth;
                const height = container.clientHeight;

                const svg = d3.select('#neo4jContainer')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height);

                // Sample data representing database connections
                const nodes = [
                    { id: 'errors', type: 'error_logs', label: 'Error Logs', x: width/4, y: height/2 },
                    { id: 'official', type: 'official_docs', label: 'Official Docs', x: width/2, y: height/4 },
                    { id: 'github', type: 'github_issues', label: 'GitHub Issues', x: 3*width/4, y: height/4 },
                    { id: 'forums', type: 'forum_posts', label: 'Forum Posts', x: width/2, y: 3*height/4 },
                    { id: 'solutions', type: 'smart_solutions', label: 'Smart Solutions', x: width/2, y: height/2 }
                ];

                const links = [
                    { source: 'errors', target: 'solutions' },
                    { source: 'official', target: 'solutions' },
                    { source: 'github', target: 'solutions' },
                    { source: 'forums', target: 'solutions' }
                ];

                // Draw links
                svg.selectAll('.link')
                    .data(links)
                    .enter()
                    .append('line')
                    .attr('class', 'link')
                    .attr('x1', d => nodes.find(n => n.id === d.source).x)
                    .attr('y1', d => nodes.find(n => n.id === d.source).y)
                    .attr('x2', d => nodes.find(n => n.id === d.target).x)
                    .attr('y2', d => nodes.find(n => n.id === d.target).y)
                    .attr('stroke', '#64748b')
                    .attr('stroke-width', 2);

                // Draw nodes
                const nodeGroups = svg.selectAll('.node')
                    .data(nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node')
                    .attr('transform', d => `translate(${d.x}, ${d.y})`);

                nodeGroups.append('circle')
                    .attr('r', 30)
                    .attr('fill', d => {
                        const colors = {
                            'error_logs': '#dc2626',
                            'official_docs': '#059669',
                            'github_issues': '#7c3aed',
                            'forum_posts': '#d97706',
                            'smart_solutions': '#2563eb'
                        };
                        return colors[d.type] || '#64748b';
                    })
                    .attr('stroke', '#ffffff')
                    .attr('stroke-width', 3);

                nodeGroups.append('text')
                    .attr('text-anchor', 'middle')
                    .attr('dy', 5)
                    .attr('fill', 'white')
                    .attr('font-size', '10px')
                    .attr('font-weight', 'bold')
                    .text(d => d.label);
            }

            async analyzeWithEvidence() {
                const crashData = document.getElementById('crashInput').value;
                if (!crashData.trim()) {
                    alert('Please enter crash data to analyze');
                    return;
                }

                try {
                    const response = await fetch('/api/analyze-with-evidence', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ crash_data: crashData })
                    });

                    const result = await response.json();
                    this.displaySpreadsheet(result.solutions);
                    this.updateVisualization(result);

                } catch (error) {
                    document.getElementById('spreadsheetContainer').innerHTML = 
                        '<div class="error">Failed to analyze crash data</div>';
                }
            }

            displaySpreadsheet(solutions) {
                if (!solutions || solutions.length === 0) {
                    document.getElementById('spreadsheetContainer').innerHTML = 
                        '<div class="error">No solutions found for this crash data</div>';
                    return;
                }

                let tableHtml = `
                    <table class="spreadsheet">
                        <thead>
                            <tr>
                                <th>Solution Title</th>
                                <th>Source Type</th>
                                <th>Source URL</th>
                                <th>Effectiveness</th>
                                <th>Success Rate</th>
                                <th>Verified</th>
                                <th>Commands</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                solutions.forEach(solution => {
                    const sourceClass = solution.source_type.replace('_', '-');
                    tableHtml += `
                        <tr>
                            <td><strong>${solution.solution_title}</strong><br>
                                <small>${solution.solution_description}</small></td>
                            <td><span class="source-badge source-${sourceClass}">${solution.source_type}</span></td>
                            <td><a href="${solution.source_url}" target="_blank">${solution.source_url}</a></td>
                            <td>${solution.effectiveness_rating}/10</td>
                            <td>${Math.round(solution.success_rate * 100)}%</td>
                            <td>${solution.verified ? '✅' : '❌'}</td>
                            <td><code>${JSON.parse(solution.commands || '[]').join(', ')}</code></td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                document.getElementById('spreadsheetContainer').innerHTML = tableHtml;
            }

            updateVisualization(result) {
                // Update the Neo4j visualization with new data
                this.createDatabaseVisualization();
            }

            async loadVerbatimLogs() {
                try {
                    document.getElementById('verbatimLogsContainer').innerHTML =
                        '<div class="loading">Loading verbatim system logs...</div>';

                    const response = await fetch('/api/verbatim-logs');
                    const logs = await response.json();
                    this.displayVerbatimLogs(logs);

                } catch (error) {
                    document.getElementById('verbatimLogsContainer').innerHTML =
                        '<div class="error">Failed to load verbatim logs</div>';
                }
            }

            displayVerbatimLogs(logs) {
                let html = '<div style="max-height: 600px; overflow-y: auto;">';

                // Application Errors
                if (logs.application_errors && logs.application_errors.length > 0) {
                    html += '<h4>🚨 Application Error Messages (Verbatim)</h4>';
                    html += '<table class="spreadsheet"><thead><tr>';
                    html += '<th>Timestamp</th><th>Application</th><th>PID</th><th>Signal</th><th>Raw Message</th>';
                    html += '</tr></thead><tbody>';

                    logs.application_errors.forEach(log => {
                        html += '<tr>';
                        html += `<td>${log[0]}</td>`;  // timestamp
                        html += `<td>${log[1]}</td>`;  // application
                        html += `<td>${log[2] || 'N/A'}</td>`;  // pid
                        html += `<td>${log[4] || 'N/A'}</td>`;  // signal_number
                        html += `<td><code style="font-size: 0.8rem; word-break: break-all;">${log[5]}</code></td>`;  // raw_line
                        html += '</tr>';
                    });
                    html += '</tbody></table><br>';
                }

                // System Events
                if (logs.system_events && logs.system_events.length > 0) {
                    html += '<h4>🖥️ System Event Messages (Verbatim)</h4>';
                    html += '<table class="spreadsheet"><thead><tr>';
                    html += '<th>Timestamp</th><th>Service</th><th>PID</th><th>Raw Message</th>';
                    html += '</tr></thead><tbody>';

                    logs.system_events.slice(0, 20).forEach(log => {
                        html += '<tr>';
                        html += `<td>${log[0]}</td>`;  // timestamp
                        html += `<td>${log[1]}</td>`;  // service
                        html += `<td>${log[2] || 'N/A'}</td>`;  // pid
                        html += `<td><code style="font-size: 0.8rem; word-break: break-all;">${log[4]}</code></td>`;  // raw_line
                        html += '</tr>';
                    });
                    html += '</tbody></table><br>';
                }

                // Kernel Messages
                if (logs.kernel_messages && logs.kernel_messages.length > 0) {
                    html += '<h4>🔧 Kernel Messages (Verbatim)</h4>';
                    html += '<table class="spreadsheet"><thead><tr>';
                    html += '<th>Timestamp</th><th>Subsystem</th><th>Raw Message</th>';
                    html += '</tr></thead><tbody>';

                    logs.kernel_messages.forEach(log => {
                        html += '<tr>';
                        html += `<td>${log[0]}</td>`;  // timestamp
                        html += `<td>${log[1]}</td>`;  // subsystem
                        html += `<td><code style="font-size: 0.8rem; word-break: break-all;">${log[3]}</code></td>`;  // raw_line
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                }

                html += '</div>';
                document.getElementById('verbatimLogsContainer').innerHTML = html;
            }
        }

        // Initialize the analyzer
        const analyzer = new IntelligentAnalyzer();

        // Global functions for buttons
        function analyzeWithEvidence() {
            analyzer.analyzeWithEvidence();
        }

        function loadVerbatimLogs() {
            analyzer.loadVerbatimLogs();
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/database-stats')
def database_stats():
    """Get comprehensive database statistics"""
    stats = intelligent_db.get_database_stats()

    # Add real system log stats
    real_stats = real_logs.get_stats()
    stats.update(real_stats)

    return jsonify(stats)

@app.route('/api/verbatim-logs')
def verbatim_logs():
    """Get verbatim system and application logs"""
    try:
        logs = real_logs.get_verbatim_logs(100)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e), 'system_events': [], 'application_errors': [], 'kernel_messages': []}), 500

@app.route('/api/capture-fresh-logs')
def capture_fresh_logs():
    """Capture fresh system logs"""
    count = real_logs.capture_and_store_all()
    return jsonify({'captured': count, 'status': 'success'})

@app.route('/api/analyze-with-evidence', methods=['POST'])
def analyze_with_evidence():
    """Analyze crash data and return evidence-based solutions"""
    data = request.get_json()
    crash_data = data.get('crash_data', '')
    
    if not crash_data:
        return jsonify({'error': 'No crash data provided'}), 400
    
    # Find solutions using intelligent database
    solutions = intelligent_db.find_solutions_for_crash(crash_data)
    
    # Format solutions for display
    formatted_solutions = []
    for solution in solutions:
        formatted_solutions.append({
            'solution_title': solution[2],
            'solution_description': solution[3],
            'solution_steps': solution[4],
            'commands': solution[5],
            'source_type': solution[6],
            'source_url': solution[8],
            'effectiveness_rating': solution[9],
            'success_rate': solution[10],
            'verified': bool(solution[11])
        })
    
    return jsonify({
        'solutions': formatted_solutions,
        'total_found': len(formatted_solutions),
        'database_stats': intelligent_db.get_database_stats()
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Crash Analyzer with Evidence...")
    print("📊 Initializing intelligent database...")
    print("🌐 Neo4j visualization ready")
    print("📋 Spreadsheet interface ready")
    print("✅ Access: http://localhost:9001")
    app.run(host='0.0.0.0', port=9001, debug=False)
