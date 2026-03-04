from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import os
import subprocess
import signal
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Directory containing your .py scripts
SCRIPTS_DIR = Path("scripts")
SCRIPTS_DIR.mkdir(exist_ok=True)

# Store the current running process
current_process = None

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Check if server is running"""
    return jsonify({"status": "ok"})

@app.route('/scripts', methods=['GET'])
def list_scripts():
    """List all .py files in the scripts directory"""
    try:
        scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
        return jsonify({"scripts": sorted(scripts)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run', methods=['POST'])
def run_script():
    """Execute a selected Python script"""
    global current_process
    
    data = request.json
    script_name = data.get('script')
    
    if not script_name:
        return jsonify({"error": "No script specified"}), 400
    
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return jsonify({"error": "Script not found"}), 404
    
    def generate():
        global current_process
        try:
            # Run the script and stream output
            current_process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output line by line
            for line in current_process.stdout:
                yield line
            
            current_process.wait()
            
            if current_process.returncode != 0:
                yield f"\n⚠️  Process exited with code {current_process.returncode}\n"
            
        except Exception as e:
            yield f"\n❌ Error: {str(e)}\n"
        finally:
            current_process = None
    
    return Response(generate(), mimetype='text/plain')

@app.route('/stop', methods=['POST'])
def stop_script():
    """Stop the currently running script"""
    global current_process
    
    if current_process:
        try:
            # Send SIGTERM to gracefully stop the process
            current_process.terminate()
            current_process.wait(timeout=5)
            return jsonify({"status": "stopped"})
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't stop
            current_process.kill()
            return jsonify({"status": "killed"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"status": "no process running"})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AG2 Script Runner Server Starting...")
    print("=" * 60)
    print(f"📁 Scripts directory: {SCRIPTS_DIR.absolute()}")
    print(f"🌐 Server running on: http://localhost:5000")
    print(f"🌐 Open in browser: http://localhost:5000")
    print("💡 Place your .py files in the 'scripts' folder")
    print("=" * 60)
    
    app.run(debug=True, port=5000, threaded=True)