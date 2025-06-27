#!/usr/bin/env python3
"""
🎨 Advanced UX Interface for Crash Analysis System
Implements modern, responsive UI with real-time updates

Features:
- Real-time crash monitoring
- Interactive solution cards
- Progress indicators
- Keyboard shortcuts
- Accessibility improvements
- Mobile-responsive design
"""

import json
import time
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import threading

class AdvancedUXInterface:
    def __init__(self, app, crash_correlator):
        self.app = app
        self.crash_correlator = crash_correlator
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self.active_connections = 0
        self.setup_routes()
        self.setup_socketio_events()
    
    def setup_routes(self):
        """Setup advanced UX routes"""
        
        @self.app.route('/advanced')
        def advanced_dashboard():
            """Advanced dashboard with real-time features"""
            return render_template_string(self.get_advanced_template())
        
        @self.app.route('/api/system-status')
        def system_status():
            """Get real-time system status"""
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'active_connections': self.active_connections,
                'database_available': self.crash_correlator.solutions_db is not None,
                'memory_usage': self.get_memory_usage(),
                'uptime': self.get_uptime()
            })
        
        @self.app.route('/api/solution-feedback', methods=['POST'])
        def solution_feedback():
            """Collect user feedback on solutions"""
            data = request.get_json()
            solution_id = data.get('solution_id')
            rating = data.get('rating')
            comment = data.get('comment', '')
            
            # Store feedback (implement database storage)
            feedback = {
                'solution_id': solution_id,
                'rating': rating,
                'comment': comment,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({'status': 'success', 'feedback_id': f'fb_{int(time.time())}'})
    
    def setup_socketio_events(self):
        """Setup WebSocket events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.active_connections += 1
            emit('status', {'message': 'Connected to real-time updates'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.active_connections -= 1
        
        @self.socketio.on('analyze_crash_realtime')
        def handle_realtime_analysis(data):
            """Handle real-time crash analysis with progress updates"""
            crash_file = data.get('crash_file')
            
            # Emit progress updates
            emit('analysis_progress', {'stage': 'starting', 'progress': 0})
            
            emit('analysis_progress', {'stage': 'reading_file', 'progress': 20})
            
            # Perform analysis
            analysis = self.crash_correlator.analyze_vscode_crash_file(crash_file)
            
            emit('analysis_progress', {'stage': 'analyzing', 'progress': 60})
            
            # Get solutions
            if 'error' not in analysis and self.crash_correlator.solutions_db:
                solutions = self.crash_correlator.solutions_db.find_solutions(
                    analysis.get('raw_crash_data', '')
                )
                analysis['intelligent_solutions'] = solutions[:5]
            
            emit('analysis_progress', {'stage': 'complete', 'progress': 100})
            emit('analysis_complete', analysis)
    
    def get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return {
                'rss': process.memory_info().rss / 1024 / 1024,  # MB
                'vms': process.memory_info().vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return {
                    'seconds': uptime_seconds,
                    'formatted': f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
                }
        except:
            return {'error': 'Unable to get uptime'}
    
    def get_advanced_template(self):
        """Get advanced HTML template with modern UX"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Advanced Crash Analysis Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --light: #f9fafb;
            --border: #e5e7eb;
            --text: #374151;
            --text-light: #6b7280;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--text);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .status-bar {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .status-item {
            background: var(--light);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-online { border-color: var(--success); color: var(--success); }
        .status-warning { border-color: var(--warning); color: var(--warning); }
        .status-error { border-color: var(--danger); color: var(--danger); }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--dark);
        }
        
        .upload-area {
            border: 2px dashed var(--border);
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: var(--primary);
            background: rgba(37, 99, 235, 0.05);
        }
        
        .upload-area.dragover {
            border-color: var(--success);
            background: rgba(16, 185, 129, 0.1);
        }
        
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-1px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--success));
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .solution-card {
            background: var(--light);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .solution-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .solution-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .solution-title {
            font-weight: 600;
            color: var(--dark);
        }
        
        .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .badge-success { background: var(--success); color: white; }
        .badge-warning { background: var(--warning); color: white; }
        .badge-danger { background: var(--danger); color: white; }
        
        .command-block {
            background: var(--dark);
            color: #e5e7eb;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
            margin: 0.5rem 0;
            position: relative;
            overflow-x: auto;
        }
        
        .copy-btn {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75rem;
        }
        
        .toast {
            position: fixed;
            top: 2rem;
            right: 2rem;
            background: var(--success);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }
        
        .toast.show {
            transform: translateX(0);
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .keyboard-shortcuts {
            position: fixed;
            bottom: 2rem;
            left: 2rem;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.75rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .keyboard-shortcuts.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Advanced Crash Analysis Dashboard</h1>
            <p>Real-time crash analysis with intelligent solutions</p>
            
            <div class="status-bar">
                <div class="status-item status-online" id="connectionStatus">
                    🟢 Connected
                </div>
                <div class="status-item" id="databaseStatus">
                    📊 Database: Loading...
                </div>
                <div class="status-item" id="memoryStatus">
                    💾 Memory: Loading...
                </div>
                <div class="status-item" id="uptimeStatus">
                    ⏱️ Uptime: Loading...
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📁 Crash File Analysis</h3>
                <div class="upload-area" id="uploadArea">
                    <div>
                        <h4>Drop crash file here or click to browse</h4>
                        <p>Supports .txt, .log, and .crash files</p>
                    </div>
                    <input type="file" id="fileInput" style="display: none;" accept=".txt,.log,.crash">
                </div>
                
                <div id="progressContainer" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText">Initializing...</p>
                </div>
                
                <button class="btn" id="analyzeBtn" disabled>
                    <span class="loading" id="loadingSpinner" style="display: none;"></span>
                    🔍 Analyze Crash
                </button>
            </div>
            
            <div class="card">
                <h3>📊 System Monitoring</h3>
                <div id="systemStats">
                    <p>Real-time system statistics will appear here...</p>
                </div>
            </div>
        </div>
        
        <div class="card" id="resultsCard" style="display: none;">
            <h3>💡 Analysis Results</h3>
            <div id="analysisResults"></div>
        </div>
    </div>
    
    <div class="keyboard-shortcuts" id="keyboardShortcuts">
        <strong>Keyboard Shortcuts:</strong><br>
        Ctrl+O: Open file<br>
        Ctrl+Enter: Analyze<br>
        Esc: Clear results<br>
        ?: Show/hide shortcuts
    </div>
    
    <div class="toast" id="toast"></div>
    
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // DOM elements
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const resultsCard = document.getElementById('resultsCard');
        const analysisResults = document.getElementById('analysisResults');
        const keyboardShortcuts = document.getElementById('keyboardShortcuts');
        
        let selectedFile = null;
        
        // Socket events
        socket.on('connect', () => {
            updateConnectionStatus('🟢 Connected', 'status-online');
            loadSystemStatus();
        });
        
        socket.on('disconnect', () => {
            updateConnectionStatus('🔴 Disconnected', 'status-error');
        });
        
        socket.on('analysis_progress', (data) => {
            updateProgress(data.progress, data.stage);
        });
        
        socket.on('analysis_complete', (data) => {
            displayResults(data);
            hideProgress();
        });
        
        // File upload handling
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleDrop);
        fileInput.addEventListener('change', handleFileSelect);
        
        function handleDragOver(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        }
        
        function handleDrop(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        }
        
        function handleFileSelect(e) {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        }
        
        function handleFile(file) {
            selectedFile = file;
            uploadArea.innerHTML = `<h4>📄 ${file.name}</h4><p>Ready to analyze</p>`;
            analyzeBtn.disabled = false;
        }
        
        // Analysis
        analyzeBtn.addEventListener('click', () => {
            if (selectedFile) {
                startAnalysis();
            }
        });
        
        function startAnalysis() {
            showProgress();
            analyzeBtn.disabled = true;
            
            // For demo, we'll use a predefined file path
            const crashFile = '/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt';
            
            socket.emit('analyze_crash_realtime', { crash_file: crashFile });
        }
        
        function showProgress() {
            progressContainer.style.display = 'block';
            document.getElementById('loadingSpinner').style.display = 'inline-block';
        }
        
        function hideProgress() {
            progressContainer.style.display = 'none';
            document.getElementById('loadingSpinner').style.display = 'none';
            analyzeBtn.disabled = false;
        }
        
        function updateProgress(progress, stage) {
            progressFill.style.width = progress + '%';
            progressText.textContent = `${stage.replace('_', ' ').toUpperCase()}: ${progress}%`;
        }
        
        function displayResults(data) {
            resultsCard.style.display = 'block';
            
            const solutions = data.intelligent_solutions || [];
            
            let html = `
                <div style="margin-bottom: 2rem;">
                    <h4>📊 Crash Analysis Summary</h4>
                    <p><strong>Type:</strong> ${data.crash_type || 'Unknown'}</p>
                    <p><strong>Severity:</strong> <span class="badge badge-${getSeverityClass(data.severity)}">${data.severity || 'Unknown'}</span></p>
                </div>
            `;
            
            if (solutions.length > 0) {
                html += '<h4>💡 Intelligent Solutions</h4>';
                solutions.forEach((solution, index) => {
                    html += createSolutionCard(solution, index);
                });
            }
            
            analysisResults.innerHTML = html;
            resultsCard.scrollIntoView({ behavior: 'smooth' });
        }
        
        function createSolutionCard(solution, index) {
            const commands = solution.commands || [];
            return `
                <div class="solution-card">
                    <div class="solution-header">
                        <div class="solution-title">${solution.solution_title || 'Unknown Solution'}</div>
                        <span class="badge badge-${getSeverityClass(solution.severity)}">${solution.severity || 'Unknown'}</span>
                    </div>
                    <p>${solution.solution_description || 'No description available'}</p>
                    ${commands.length > 0 ? `
                        <div style="margin-top: 1rem;">
                            <strong>Commands:</strong>
                            ${commands.map(cmd => `
                                <div class="command-block">
                                    <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(cmd)}')">Copy</button>
                                    ${escapeHtml(cmd)}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        function getSeverityClass(severity) {
            if (!severity) return 'warning';
            const s = severity.toLowerCase();
            if (s.includes('high') || s.includes('critical')) return 'danger';
            if (s.includes('medium')) return 'warning';
            return 'success';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Command copied to clipboard!');
            });
        }
        
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
        
        function updateConnectionStatus(text, className) {
            const status = document.getElementById('connectionStatus');
            status.textContent = text;
            status.className = `status-item ${className}`;
        }
        
        function loadSystemStatus() {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('databaseStatus').textContent = 
                        `📊 Database: ${data.database_available ? 'Available' : 'Unavailable'}`;
                    
                    if (data.memory_usage && !data.memory_usage.error) {
                        document.getElementById('memoryStatus').textContent = 
                            `💾 Memory: ${data.memory_usage.rss.toFixed(1)}MB (${data.memory_usage.percent.toFixed(1)}%)`;
                    }
                    
                    if (data.uptime && !data.uptime.error) {
                        document.getElementById('uptimeStatus').textContent = 
                            `⏱️ Uptime: ${data.uptime.formatted}`;
                    }
                });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                fileInput.click();
            } else if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                if (!analyzeBtn.disabled) analyzeBtn.click();
            } else if (e.key === 'Escape') {
                resultsCard.style.display = 'none';
            } else if (e.key === '?') {
                keyboardShortcuts.classList.toggle('show');
            }
        });
        
        // Auto-refresh system status
        setInterval(loadSystemStatus, 30000);
    </script>
</body>
</html>
        '''

def main():
    """Test advanced UX interface"""
    from flask import Flask
    app = Flask(__name__)
    
    # Mock crash correlator
    class MockCorrelator:
        def __init__(self):
            self.solutions_db = True
    
    correlator = MockCorrelator()
    ux = AdvancedUXInterface(app, correlator)
    
    print("🎨 Advanced UX Interface initialized")
    print("📱 Access: http://localhost:5000/advanced")
    
    ux.socketio.run(app, debug=True, port=5000)

if __name__ == '__main__':
    main()
