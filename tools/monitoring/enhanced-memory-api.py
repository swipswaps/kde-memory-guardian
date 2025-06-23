#!/usr/bin/env python3
"""
Enhanced Memory Protection Metrics API with WebSocket Support
Real-time memory protection data for dashboard integration
"""

import json, subprocess, time, threading
try:
    import psutil
    from flask import Flask, jsonify
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
except ImportError:
    print("Missing dependencies. Install with: pip install psutil flask flask-cors flask-socketio")
    exit(1)

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for real-time monitoring
monitoring_active = False
monitoring_thread = None

def get_protection_status():
    """Get current protection tier status"""
    try:
        result = subprocess.run([
            './tools/memory-pressure/unified-memory-manager.sh', 'status'
        ], capture_output=True, text=True, cwd='/home/owner/Documents/6854a1da-e23c-8008-a9fc-76b7fa3c1f92/kde-memory-guardian')
        
        output = result.stdout
        
        # Parse protection status
        earlyoom_active = "✅ Tier 1 (earlyoom): ACTIVE" in output
        nohang_active = "✅ Tier 2 (nohang): ACTIVE" in output
        systemd_oomd_active = "✅ Tier 3 (systemd-oomd): ACTIVE" in output
        
        return {
            'tier1_earlyoom': earlyoom_active,
            'tier2_nohang': nohang_active,
            'tier3_systemd_oomd': systemd_oomd_active,
            'total_active_tiers': sum([earlyoom_active, nohang_active, systemd_oomd_active])
        }
    except Exception as e:
        return {'error': str(e)}

def get_memory_stats():
    """Get current memory statistics"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'cached': getattr(memory, 'cached', 0),
                'buffers': getattr(memory, 'buffers', 0)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_top_processes():
    """Get top memory-consuming processes with OOM scores"""
    try:
        result = subprocess.run(['oom-sort', '--num', '5'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
        processes = []
        
        for line in lines:
            if line.strip():
                parts = line.split(None, 7)
                if len(parts) >= 7:
                    processes.append({
                        'oom_score': int(parts[0]),
                        'name': parts[4],
                        'vmrss': parts[5],
                        'pid': int(parts[3])
                    })
        
        return processes
    except Exception as e:
        return []

def get_comprehensive_data():
    """Get all data for dashboard"""
    return {
        'timestamp': time.time(),
        'protection': get_protection_status(),
        'memory': get_memory_stats(),
        'top_processes': get_top_processes()
    }

def monitoring_worker():
    """Background worker for real-time monitoring"""
    global monitoring_active
    while monitoring_active:
        try:
            data = get_comprehensive_data()
            socketio.emit('memory_update', data)
            time.sleep(2)  # Update every 2 seconds
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(5)

# REST API Endpoints
@app.route('/api/memory/status')
def memory_status():
    """Get comprehensive memory protection status"""
    return jsonify(get_comprehensive_data())

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'enhanced-memory-api',
        'websocket_enabled': True
    })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'status': 'connected', 'message': 'Memory monitoring ready'})
    # Send initial data
    emit('memory_update', get_comprehensive_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """Start real-time monitoring"""
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_worker)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        emit('monitoring_started', {'status': 'started'})
        print('Real-time monitoring started')

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop real-time monitoring"""
    global monitoring_active
    monitoring_active = False
    emit('monitoring_stopped', {'status': 'stopped'})
    print('Real-time monitoring stopped')

if __name__ == '__main__':
    print("🛡️ Enhanced Memory Protection API Starting...")
    print("📊 REST API endpoints:")
    print("   http://localhost:3002/api/memory/status")
    print("   http://localhost:3002/api/health")
    print("🔌 WebSocket endpoint:")
    print("   ws://localhost:3002/socket.io/")
    print("🎨 Real-time integration for Material UI dashboard")
    
    socketio.run(app, host='0.0.0.0', port=3002, debug=False)
