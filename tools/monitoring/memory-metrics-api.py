#!/usr/bin/env python3
"""Memory Protection Metrics API"""
import json, subprocess, time
try:
    import psutil
    from flask import Flask, jsonify
    from flask_cors import CORS
except ImportError:
    print("Missing dependencies. Install with: pip install psutil flask flask-cors")
    exit(1)

app = Flask(__name__)
CORS(app)

@app.route('/api/memory/status')
def memory_status():
    memory = psutil.virtual_memory()
    return jsonify({
        'timestamp': time.time(),
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
    })

if __name__ == '__main__':
    print("🛡️ Memory API on http://localhost:3002")
    app.run(host='0.0.0.0', port=3002, debug=False)
