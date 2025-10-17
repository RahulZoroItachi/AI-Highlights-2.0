#!/usr/bin/env python3
"""
Simple API server to handle frontend requests for updating inputs.json and running analysis
"""

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import json
import os
import subprocess
import sys
import threading
import time
import signal
from datetime import datetime
from pathlib import Path
import queue
from dotenv import load_dotenv

# Load environment variables from .env file
env_file_path = Path(__file__).parent / '.env'
load_dotenv(env_file_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Path to inputs.json file
INPUTS_FILE = Path(__file__).parent / 'inputs.json'

# Global variables for analysis process management
analysis_processes = {}  # Store running processes by session ID
analysis_outputs = {}    # Store output queues by session ID

@app.route('/api/inputs', methods=['GET'])
def get_inputs():
    """Get current inputs.json data"""
    try:
        if INPUTS_FILE.exists():
            with open(INPUTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({"success": True, "data": data})
        else:
            return jsonify({"success": False, "error": "inputs.json not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/scenarios')
def get_scenarios():
    """Get all available scenarios from inputs.json"""
    try:
        from inputs import get_available_scenarios
        scenarios = get_available_scenarios()
        
        return jsonify({
            "success": True,
            "scenarios": scenarios
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get scenarios: {str(e)}"
        })

@app.route('/api/inputs', methods=['POST'])
def update_inputs():
    """Update inputs.json with new data"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        # Create backup of existing file
        if INPUTS_FILE.exists():
            backup_file = INPUTS_FILE.with_suffix('.json.backup')
            import shutil
            shutil.copy2(INPUTS_FILE, backup_file)
            print(f"📋 Created backup: {backup_file}")
        
        # Write new data to inputs.json
        with open(INPUTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated inputs.json successfully")
        return jsonify({"success": True, "message": "inputs.json updated successfully"})
        
    except Exception as e:
        print(f"❌ Error updating inputs.json: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/inputs/scenario', methods=['POST'])
def update_scenario():
    """Update a specific scenario in inputs.json"""
    try:
        data = request.json
        scenario = data.get('scenario')
        scenario_data = data.get('data')
        
        if not scenario or not scenario_data:
            return jsonify({"success": False, "error": "Missing scenario or data"})
        
        # Load existing inputs.json
        if INPUTS_FILE.exists():
            with open(INPUTS_FILE, 'r', encoding='utf-8') as f:
                inputs = json.load(f)
        else:
            inputs = {}
        
        # Update the specific scenario
        inputs[scenario] = scenario_data
        
        # Create backup
        if INPUTS_FILE.exists():
            backup_file = INPUTS_FILE.with_suffix('.json.backup')
            import shutil
            shutil.copy2(INPUTS_FILE, backup_file)
        
        # Write updated data
        with open(INPUTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(inputs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated scenario '{scenario}' in inputs.json")
        return jsonify({"success": True, "message": f"Scenario '{scenario}' updated successfully"})
        
    except Exception as e:
        print(f"❌ Error updating scenario: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/analysis/start', methods=['POST'])
def start_analysis():
    """Start analysis process and return session ID"""
    try:
        data = request.json
        scenario = data.get('scenario')
        
        if not scenario:
            return jsonify({"success": False, "error": "Missing scenario"})
        
        # Generate unique session ID
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        # Create output queue for this session
        output_queue = queue.Queue()
        analysis_outputs[session_id] = output_queue
        
        # Prepare environment variables for main.py
        # Re-load .env file to get the latest values (in case they were updated via settings)
        from dotenv import load_dotenv
        env_file_path = Path(__file__).parent / '.env'
        load_dotenv(env_file_path, override=True)
        
        env = os.environ.copy()  # Start with all current environment variables (now includes fresh .env values)
        env['ANALYSIS_SCENARIO'] = scenario
        # LLM_PROVIDER should now be loaded from the fresh .env file
        if 'LLM_PROVIDER' not in env or not env['LLM_PROVIDER']:
            env['LLM_PROVIDER'] = 'claude'  # Default fallback
        env['LOAD_PREVIOUS_PLAN'] = str(data.get('load_previous_plan', '')) if data.get('load_previous_plan') else ''
        env['LOAD_PREVIOUS_DATA'] = str(data.get('load_previous_data', '')) if data.get('load_previous_data') else ''
        env['REPORT_ANALYSIS_VERSION'] = str(data.get('report_analysis_version', '')) if data.get('report_analysis_version') else ''
        
        # Ensure critical environment variables are available
        # Always required
        required_env_vars = [
            'THOUGHTSPOT_BASE_URL',
            'THOUGHTSPOT_AUTH_TOKEN'
        ]
        
        # LLM provider specific (use from environment, not from request)
        llm_provider = env.get('LLM_PROVIDER', 'claude')
        print(f"🤖 Using LLM Provider: {llm_provider.upper()}")
        
        if llm_provider == 'claude':
            required_env_vars.append('CLAUDE_API_KEY')
        elif llm_provider == 'openai':
            required_env_vars.append('OPENAI_API_KEY')
        elif llm_provider == 'gemini':
            required_env_vars.append('GEMINI_API_KEY')
        
        missing_vars = []
        for var in required_env_vars:
            if var not in env or not env[var]:
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            print(f"❌ {error_msg}")  # Also print to server console
            return jsonify({"success": False, "error": error_msg})
        
        print(f"🔧 Environment variables configured for {llm_provider}")
        
        # Start analysis process
        def run_analysis():
            try:
                # Use the same Python executable that's running the API server
                python_executable = sys.executable
                
                process = subprocess.Popen(
                    [python_executable, 'main.py'],  # Use same Python executable
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=0,  # Unbuffered
                    env=env,
                    cwd=Path(__file__).parent,
                    preexec_fn=None,  # Don't change process group
                    start_new_session=False  # Keep in same session for better cleanup
                )
                
                analysis_processes[session_id] = process
                
                # Read output line by line and put in queue with timeout monitoring
                try:
                    import select
                    import time
                    last_output_time = time.time()
                    timeout_seconds = 600  # 10 minutes timeout for no output (increased from 5 minutes)
                    
                    while True:
                        # Check if process is still running
                        if process.poll() is not None:
                            break
                            
                        # Check for available output with timeout
                        ready, _, _ = select.select([process.stdout], [], [], 1.0)
                        
                        if ready:
                            line = process.stdout.readline()
                            if not line:
                                break
                            output_queue.put(line.strip())
                            last_output_time = time.time()
                        else:
                            # Send periodic heartbeat to show process is still alive
                            current_time = time.time()
                            time_since_last_output = current_time - last_output_time
                            
                            # Send heartbeat every 30 seconds
                            if int(time_since_last_output) % 30 == 0 and int(time_since_last_output) > 0:
                                output_queue.put(f"⏳ Analysis in progress... (no output for {int(time_since_last_output)} seconds)")
                            
                            # Check for timeout
                            if time_since_last_output > timeout_seconds:
                                output_queue.put(f"⚠️ Warning: No output for {timeout_seconds} seconds, process may be stuck")
                                output_queue.put(f"🔧 Debug: Terminating process due to timeout")
                                process.terminate()
                                try:
                                    process.wait(timeout=10)
                                except subprocess.TimeoutExpired:
                                    process.kill()
                                    process.wait()
                                output_queue.put("__ANALYSIS_ERROR__: Process terminated due to timeout (no output for 10 minutes)")
                                return
                                
                except Exception as read_error:
                    pass  # Suppress debug error output
                
                # Wait for process to complete
                return_code = process.wait()
                
                # Signal completion
                if return_code == 0:
                    # Try to read the latest report file for this scenario
                    report_content = None
                    try:
                        import glob
                        import os
                        # Look for the most recent report file for this scenario
                        analysis_scenario = None
                        
                        # Extract scenario from environment or process args if available
                        for env_var in os.environ:
                            if 'SCENARIO' in env_var or 'ANALYSIS_SCENARIO' in env_var:
                                analysis_scenario = os.environ[env_var]
                                break
                        
                        # If no scenario found in environment, try to extract from command line args
                        if not analysis_scenario:
                            output_queue.put(f"🔧 Debug: No scenario found in environment variables")
                        
                        if analysis_scenario:
                            # Look for report files in scenario-specific directory
                            report_pattern = f"{analysis_scenario}/{analysis_scenario}_v*/report_*.txt"
                            report_files = glob.glob(report_pattern)
                            
                            if not report_files:
                                # Try alternative pattern
                                report_pattern = f"{analysis_scenario}/{analysis_scenario}_v*/{analysis_scenario}_report_*.txt"
                                report_files = glob.glob(report_pattern)
                            
                            if report_files:
                                # Get the most recent report file
                                latest_report = max(report_files, key=os.path.getctime)
                                with open(latest_report, 'r', encoding='utf-8') as f:
                                    report_content = f.read()
                            else:
                                pass  # No report files found
                    except Exception as report_error:
                        pass  # Suppress report error debug output
                    
                    # Send completion with report content if available
                    if report_content:
                        output_queue.put(f"__ANALYSIS_COMPLETE__:{report_content}")
                    else:
                        output_queue.put("__ANALYSIS_COMPLETE__")
                else:
                    output_queue.put(f"__ANALYSIS_ERROR__: Process exited with code {return_code}")
                    
            except Exception as e:
                output_queue.put(f"__ANALYSIS_ERROR__: {str(e)}")
            finally:
                # Clean up
                if session_id in analysis_processes:
                    del analysis_processes[session_id]
                output_queue.put("Session cleanup completed")
        
        # Start analysis in background thread with better error handling
        thread = threading.Thread(target=run_analysis, name=f"analysis-{session_id}")
        thread.daemon = False  # Don't make it daemon so it can complete properly
        thread.start()
        
        # Store thread reference for cleanup
        analysis_processes[f"{session_id}_thread"] = thread
        
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "message": f"Analysis started for scenario: {scenario}"
        })
        
    except Exception as e:
        print(f"❌ Error starting analysis: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/analysis/progress/<session_id>')
def get_analysis_progress(session_id):
    """Stream analysis progress for a session"""
    def generate():
        if session_id not in analysis_outputs:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
        
        output_queue = analysis_outputs[session_id]
        
        while True:
            try:
                # Get output with timeout
                line = output_queue.get(timeout=1)
                
                if line.startswith("__ANALYSIS_COMPLETE__"):
                    # Check if there's report content included
                    completion_data = {'type': 'complete', 'message': 'Analysis completed successfully!'}
                    
                    if ":" in line:
                        report_content = line.split(":", 1)[1]
                        completion_data['report_content'] = report_content
                    
                    yield f"data: {json.dumps(completion_data)}\n\n"
                    break
                elif line.startswith("__ANALYSIS_ERROR__"):
                    error_msg = line.replace("__ANALYSIS_ERROR__: ", "")
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    break
                else:
                    yield f"data: {json.dumps({'type': 'output', 'message': line})}\n\n"
                    
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
                # Check if process is still running
                if session_id not in analysis_processes:
                    break
        
        # Clean up
        if session_id in analysis_outputs:
            del analysis_outputs[session_id]
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/analysis/stop/<session_id>', methods=['POST'])
def stop_analysis(session_id):
    """Stop running analysis process"""
    try:
        if session_id not in analysis_processes:
            return jsonify({"success": False, "error": "Analysis session not found"})
        
        process = analysis_processes[session_id]
        
        # Terminate the process
        print(f"🛑 Terminating analysis process {process.pid} for session {session_id}")
        process.terminate()
        
        # Wait a bit for graceful termination
        try:
            process.wait(timeout=10)
            print(f"✅ Process {process.pid} terminated gracefully")
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate gracefully
            print(f"🔥 Force killing process {process.pid}")
            process.kill()
            process.wait()
        
        # Clean up both process and thread references
        if session_id in analysis_processes:
            del analysis_processes[session_id]
        if f"{session_id}_thread" in analysis_processes:
            thread = analysis_processes[f"{session_id}_thread"]
            # Note: thread will clean up naturally when process exits
            del analysis_processes[f"{session_id}_thread"]
            
        if session_id in analysis_outputs:
            analysis_outputs[session_id].put("__ANALYSIS_ERROR__: Analysis stopped by user")
        
        return jsonify({"success": True, "message": "Analysis stopped successfully"})
        
    except Exception as e:
        print(f"❌ Error stopping analysis: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/report/<scenario>/<int:version>', methods=['GET'])
def get_report_content(scenario, version):
    """Get the report content for a specific scenario and version"""
    try:
        import glob
        from pathlib import Path
        
        # Look for report files in the scenario version directory
        version_str = str(version).zfill(3)  # Convert to 3-digit format (e.g., 001, 002)
        scenario_dir = Path(__file__).parent / scenario
        
        if not scenario_dir.exists():
            return jsonify({
                "success": False, 
                "error": f"Scenario directory '{scenario}' not found"
            })
        
        # Try different report file patterns
        report_patterns = [
            f"{scenario}_v{version_str}/{scenario}_report_*.txt",
            f"{scenario}_v{version_str}/report_*.txt",
            f"{scenario}_report_v{version_str}_*.txt"
        ]
        
        report_file = None
        for pattern in report_patterns:
            report_files = list(scenario_dir.glob(pattern))
            if report_files:
                # Get the most recent report file if multiple exist
                report_file = max(report_files, key=lambda f: f.stat().st_mtime)
                break
        
        if not report_file or not report_file.exists():
            return jsonify({
                "success": False,
                "error": f"Report file not found for {scenario} version {version}"
            })
        
        # Read the report content
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        return jsonify({
            "success": True,
            "scenario": scenario,
            "version": version,
            "report_content": report_content,
            "file_path": str(report_file.relative_to(Path(__file__).parent))
        })
        
    except Exception as e:
        print(f"❌ Error getting report content: {e}")
        return jsonify({
            "success": False,
            "error": f"Error reading report: {str(e)}"
        })

@app.route('/api/versions/<scenario>', methods=['GET'])
def get_scenario_versions(scenario):
    """Get available versions for a scenario"""
    try:
        scenario_dir = Path(__file__).parent / scenario
        if not scenario_dir.exists():
            return jsonify({"success": False, "error": f"Scenario directory '{scenario}' not found"})
        
        versions = {
            "plans": [],
            "data": [],
            "analysis": [],
            "reports": []
        }
        
        # Find version directories (e.g., pg_v001, pg_v002)
        version_dirs = []
        for item in scenario_dir.iterdir():
            if item.is_dir() and item.name.startswith(f"{scenario}_v"):
                try:
                    version_num = int(item.name.split('_v')[1])
                    version_dirs.append((version_num, item))
                except (IndexError, ValueError):
                    continue
        
        # Sort by version number
        version_dirs.sort(key=lambda x: x[0])
        
        # Check each version directory for files
        for version_num, version_dir in version_dirs:
            has_plan = False
            has_data = False
            has_analysis = False
            has_report = False
            
            for file in version_dir.iterdir():
                if file.is_file():
                    filename = file.name
                    if 'plan' in filename and filename.endswith('.json'):
                        has_plan = True
                    elif 'data' in filename and filename.endswith('.json'):
                        has_data = True
                    elif 'analysis' in filename and filename.endswith('.json'):
                        has_analysis = True
                    elif 'report' in filename and filename.endswith('.txt'):
                        has_report = True
            
            if has_plan:
                versions["plans"].append(version_num)
            if has_data:
                versions["data"].append(version_num)
            if has_analysis:
                versions["analysis"].append(version_num)
            if has_report:
                versions["reports"].append(version_num)
        
        # Also check root scenario directory for older format files
        for file in scenario_dir.iterdir():
            if file.is_file():
                filename = file.name
                # Look for files like pg_plan_v001_timestamp.json
                if 'plan_v' in filename and filename.endswith('.json'):
                    try:
                        version_part = filename.split('plan_v')[1].split('_')[0]
                        version_num = int(version_part)
                        if version_num not in versions["plans"]:
                            versions["plans"].append(version_num)
                    except (IndexError, ValueError):
                        continue
                elif 'data_v' in filename and filename.endswith('.json'):
                    try:
                        version_part = filename.split('data_v')[1].split('_')[0]
                        version_num = int(version_part)
                        if version_num not in versions["data"]:
                            versions["data"].append(version_num)
                    except (IndexError, ValueError):
                        continue
                elif 'analysis_v' in filename and filename.endswith('.json'):
                    try:
                        version_part = filename.split('analysis_v')[1].split('_')[0]
                        version_num = int(version_part)
                        if version_num not in versions["analysis"]:
                            versions["analysis"].append(version_num)
                    except (IndexError, ValueError):
                        continue
                elif 'report_v' in filename and filename.endswith('.txt'):
                    try:
                        version_part = filename.split('report_v')[1].split('_')[0]
                        version_num = int(version_part)
                        if version_num not in versions["reports"]:
                            versions["reports"].append(version_num)
                    except (IndexError, ValueError):
                        continue
        
        # Sort all version lists
        versions["plans"].sort(reverse=True)  # Latest first
        versions["data"].sort(reverse=True)   # Latest first
        versions["analysis"].sort(reverse=True)  # Latest first
        versions["reports"].sort(reverse=True)  # Latest first
        
        return jsonify({
            "success": True, 
            "scenario": scenario,
            "versions": versions
        })
        
    except Exception as e:
        print(f"❌ Error getting scenario versions: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/populate-inputs', methods=['POST'])
def populate_inputs():
    """Trigger input population from liveboard ID"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        liveboard_id = data.get('liveboard_id', '').strip()
        worksheet_id = data.get('worksheet_id', '').strip() if data.get('worksheet_id') else None  # Optional field
        
        if not liveboard_id:
            return jsonify({"success": False, "error": "Liveboard ID is required"})
        
        print(f"🚀 Starting input population for liveboard: {liveboard_id}")
        if worksheet_id:
            print(f"📋 Optional worksheet ID provided: {worksheet_id}")
        else:
            print(f"📋 No worksheet ID provided - will be auto-detected from liveboard")
        
        # Generate a unique session ID for this population process
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        # Create output queue for streaming progress
        output_queue = queue.Queue()
        analysis_outputs[session_id] = output_queue
        
        # Prepare environment variables for the subprocess
        env = os.environ.copy()  # Start with all current environment variables
        env['LIVEBOARD_ID'] = liveboard_id
        if worksheet_id:
            env['WORKSHEET_ID'] = worksheet_id
        
        # Ensure critical environment variables are available
        required_env_vars = [
            'THOUGHTSPOT_BASE_URL',
            'THOUGHTSPOT_AUTH_TOKEN',
            'CLAUDE_API_KEY'  # Assuming input population uses Claude
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if var not in env or not env[var]:
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            print(f"❌ {error_msg}")
            return jsonify({"success": False, "error": error_msg})
        
        print(f"🔧 Debug: Environment variables configured for input population")
        
        # Start input population process
        def run_input_population():
            try:
                output_queue.put(f"🔧 Debug: Starting input population with liveboard_id={liveboard_id}")
                output_queue.put(f"🔧 Debug: Working directory: {Path(__file__).parent}")
                output_queue.put(f"🔧 Debug: Python executable: {sys.executable}")
                
                # Use the same Python executable that's running the API server
                python_executable = sys.executable
                
                # Create a simple script to call the input_populator function
                script_content = f'''
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
print("🔧 Loading environment variables...")
load_dotenv(Path(__file__).parent / ".env")

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Add the input_populator directory to Python path  
input_populator_dir = backend_dir / "input_populator"
sys.path.insert(0, str(input_populator_dir))

# Verify critical environment variables are loaded
required_vars = ['THOUGHTSPOT_BASE_URL', 'THOUGHTSPOT_AUTH_TOKEN', 'CLAUDE_API_KEY']
missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing environment variables: {{missing_vars}}")
    sys.exit(1)
else:
    print(f"✅ All required environment variables are loaded")

try:
    from input_invoke_api import export_and_extract_liveboard
    
    liveboard_id = os.getenv('LIVEBOARD_ID')
    print(f"📋 Processing liveboard: {{liveboard_id}}")
    
    # Call the input population function
    result = export_and_extract_liveboard(liveboard_id)
    
    print("✅ Input population completed successfully")
    print(f"📊 Result: {{result}}")
    
except Exception as e:
    print(f"❌ Error in input population: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
                
                # Write the script to a temporary file
                script_path = Path(__file__).parent / f"temp_populate_{session_id}.py"
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                try:
                    process = subprocess.Popen(
                        [python_executable, str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=0,  # Unbuffered
                        env=env,
                        cwd=Path(__file__).parent,
                        preexec_fn=None,
                        start_new_session=False
                    )
                    
                    analysis_processes[session_id] = process
                    output_queue.put(f"🔧 Debug: Process started with PID {process.pid}")
                    
                    # Read output line by line and put in queue with timeout monitoring
                    try:
                        import select
                        import time
                        last_output_time = time.time()
                        timeout_seconds = 600  # 10 minutes timeout
                        
                        while True:
                            # Check if process is still running
                            if process.poll() is not None:
                                break
                                
                            # Check for available output with timeout
                            ready, _, _ = select.select([process.stdout], [], [], 1.0)
                            
                            if ready:
                                line = process.stdout.readline()
                                if not line:
                                    break
                                output_queue.put(line.strip())
                                last_output_time = time.time()
                            else:
                                # Send periodic heartbeat to show process is still alive
                                current_time = time.time()
                                time_since_last_output = current_time - last_output_time
                                
                                # Send heartbeat every 30 seconds
                                if int(time_since_last_output) % 30 == 0 and int(time_since_last_output) > 0:
                                    output_queue.put(f"⏳ Input population in progress... (no output for {int(time_since_last_output)} seconds)")
                                
                                # Check for timeout
                                if time_since_last_output > timeout_seconds:
                                    output_queue.put(f"⚠️ Warning: No output for {timeout_seconds} seconds, process may be stuck")
                                    output_queue.put(f"🔧 Debug: Terminating process due to timeout")
                                    process.terminate()
                                    try:
                                        process.wait(timeout=10)
                                    except subprocess.TimeoutExpired:
                                        process.kill()
                                        process.wait()
                                    output_queue.put("__POPULATION_ERROR__: Process terminated due to timeout (no output for 10 minutes)")
                                    return
                                    
                    except Exception as read_error:
                        output_queue.put(f"🔧 Debug: Error reading output: {read_error}")
                    
                    # Wait for process to complete
                    return_code = process.wait()
                    output_queue.put(f"🔧 Debug: Process completed with return code {return_code}")
                    
                    # Signal completion
                    if return_code == 0:
                        output_queue.put("__POPULATION_COMPLETE__")
                    else:
                        output_queue.put(f"__POPULATION_ERROR__: Process exited with code {return_code}")
                        
                finally:
                    # Clean up temporary script file
                    try:
                        if script_path.exists():
                            script_path.unlink()
                            output_queue.put(f"🔧 Debug: Cleaned up temporary script")
                    except Exception as cleanup_error:
                        output_queue.put(f"⚠️ Warning: Could not clean up temporary script: {cleanup_error}")
                        
            except Exception as e:
                output_queue.put(f"__POPULATION_ERROR__: {str(e)}")
                output_queue.put(f"🔧 Debug: Exception in run_input_population: {e}")
            finally:
                # Clean up
                if session_id in analysis_processes:
                    del analysis_processes[session_id]
                output_queue.put("Session cleanup completed")
        
        # Start input population in background thread
        thread = threading.Thread(target=run_input_population, name=f"populate-{session_id}")
        thread.daemon = False
        thread.start()
        
        # Store thread reference for cleanup
        analysis_processes[f"{session_id}_thread"] = thread
        
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "message": f"Input population started for liveboard: {liveboard_id}"
        })
        
    except Exception as e:
        print(f"❌ Error starting input population: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/populate-progress/<session_id>')
def get_populate_progress(session_id):
    """Stream input population progress for a session"""
    def generate():
        if session_id not in analysis_outputs:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
            
        output_queue = analysis_outputs[session_id]
        
        try:
            while True:
                try:
                    # Get message from queue with timeout
                    message = output_queue.get(timeout=1)
                    
                    if message.startswith("__POPULATION_COMPLETE__"):
                        yield f"data: {json.dumps({'complete': True, 'message': 'Input population completed successfully'})}\n\n"
                        break
                    elif message.startswith("__POPULATION_ERROR__"):
                        error_msg = message.replace("__POPULATION_ERROR__: ", "")
                        yield f"data: {json.dumps({'error': True, 'message': error_msg})}\n\n"
                        break
                    else:
                        yield f"data: {json.dumps({'output': message})}\n\n"
                        
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                    continue
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': True, 'message': f'Stream error: {str(e)}'})}\n\n"
        finally:
            # Clean up
            if session_id in analysis_outputs:
                del analysis_outputs[session_id]
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/create-scenario', methods=['POST'])
def create_scenario():
    """Create a new scenario and trigger input population from liveboard"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        scenario_name = data.get('scenario_name', '').strip()
        liveboard_id = data.get('liveboard_id', '').strip()
        
        if not scenario_name:
            return jsonify({"success": False, "error": "Scenario name is required"})
        if not liveboard_id:
            return jsonify({"success": False, "error": "Liveboard ID is required"})
        
        print(f"🚀 Creating new scenario '{scenario_name}' with liveboard: {liveboard_id}")
        
        # Generate a unique session ID for this scenario creation process
        import uuid
        session_id = str(uuid.uuid4())[:8]
        
        # Create output queue for streaming progress
        output_queue = queue.Queue()
        analysis_outputs[session_id] = output_queue
        
        # Prepare environment variables for the subprocess
        env = os.environ.copy()  # Start with all current environment variables
        env['LIVEBOARD_ID'] = liveboard_id
        env['SCENARIO_NAME'] = scenario_name
        
        # Ensure critical environment variables are available
        required_env_vars = [
            'THOUGHTSPOT_BASE_URL',
            'THOUGHTSPOT_AUTH_TOKEN',
            'CLAUDE_API_KEY'  # Assuming input population uses Claude
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if var not in env or not env[var]:
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            print(f"❌ {error_msg}")
            return jsonify({"success": False, "error": error_msg})
        
        print(f"🔧 Debug: Environment variables configured for scenario creation")
        
        # Start scenario creation process
        def run_scenario_creation():
            try:
                output_queue.put(f"🔧 Debug: Starting scenario creation with scenario_name={scenario_name}, liveboard_id={liveboard_id}")
                output_queue.put(f"🔧 Debug: Working directory: {Path(__file__).parent}")
                output_queue.put(f"🔧 Debug: Python executable: {sys.executable}")
                
                # Use the same Python executable that's running the API server
                python_executable = sys.executable
                
                # Create a script to call the input_populator function with scenario parameters
                script_content = f'''
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
print("🔧 Loading environment variables...")
load_dotenv(Path(__file__).parent / ".env")

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Add the input_populator directory to Python path  
input_populator_dir = backend_dir / "input_populator"
sys.path.insert(0, str(input_populator_dir))

# Verify critical environment variables are loaded
required_vars = ['THOUGHTSPOT_BASE_URL', 'THOUGHTSPOT_AUTH_TOKEN', 'CLAUDE_API_KEY']
missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing environment variables: {{missing_vars}}")
    sys.exit(1)
else:
    print(f"✅ All required environment variables are loaded")

try:
    # Add the input_populator directory to the path for imports
    import sys
    from pathlib import Path
    input_populator_path = Path(__file__).parent / 'input_populator'
    if str(input_populator_path) not in sys.path:
        sys.path.insert(0, str(input_populator_path))
    
    from input_invoke_api import export_and_extract_liveboard
    print("✅ Successfully imported input population module")
    
    scenario_name = os.getenv('SCENARIO_NAME')
    liveboard_id = os.getenv('LIVEBOARD_ID')
    
    print(f"📋 Creating scenario: {{scenario_name}}")
    print(f"📋 Processing liveboard: {{liveboard_id}}")
    
    # Call the input population function with scenario name as liveboard_name
    result = export_and_extract_liveboard(liveboard_id, scenario_name)
    
    if result and result.get('analysis_file'):
        # Load the analysis file to extract the inputs
        analysis_file = result['analysis_file']
        print(f"📊 Loading analysis results from: {{analysis_file}}")
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Convert analysis data to inputs.json format
        inputs_data = {{
            'tml_filename': 'NA',
            'liveboard_id': liveboard_id,
            'worksheet_id': 'NA',  # Will be extracted from analysis if available
            'kpi': str(analysis_data.get('kpis', 'Key performance indicators extracted from the liveboard')),
            'attributes': str(analysis_data.get('attributes', 'Key attributes for analysis')),
            'aggregations': 'Count and sum aggregations as needed',
            'date_column': str(analysis_data.get('date_column', 'Date column for temporal analysis')),
            'goal': str(analysis_data.get('goal', 'Business goal extracted from the liveboard')),
            'user_context': str(analysis_data.get('user_context', 'User context and requirements')),
            'report_format': 'Standard report format with executive summary and detailed analysis'
        }}
        
        # Load current inputs.json
        inputs_file = backend_dir / 'inputs.json'
        if inputs_file.exists():
            with open(inputs_file, 'r', encoding='utf-8') as f:
                current_inputs = json.load(f)
        else:
            current_inputs = {{}}
        
        # Add the new scenario
        current_inputs[scenario_name] = inputs_data
        
        # Save updated inputs.json
        with open(inputs_file, 'w', encoding='utf-8') as f:
            json.dump(current_inputs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Scenario '{{scenario_name}}' created and added to inputs.json")
        print(f"📊 Extracted inputs: {{json.dumps(inputs_data, indent=2)}}")
        
    else:
        print("❌ Failed to extract inputs from liveboard")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Error in scenario creation: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
                
                # Write the script to a temporary file
                script_path = Path(__file__).parent / f"temp_create_scenario_{session_id}.py"
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                try:
                    process = subprocess.Popen(
                        [python_executable, str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=0,  # Unbuffered
                        env=env,
                        cwd=Path(__file__).parent,
                        preexec_fn=None,
                        start_new_session=False
                    )
                    
                    analysis_processes[session_id] = process
                    output_queue.put(f"🔧 Debug: Process started with PID {process.pid}")
                    
                    # Read output line by line and put in queue with timeout monitoring
                    try:
                        import select
                        import time
                        last_output_time = time.time()
                        timeout_seconds = 600  # 10 minutes timeout
                        
                        while True:
                            # Check if process is still running
                            if process.poll() is not None:
                                break
                                
                            # Check for available output with timeout
                            ready, _, _ = select.select([process.stdout], [], [], 1.0)
                            
                            if ready:
                                line = process.stdout.readline()
                                if not line:
                                    break
                                output_queue.put(line.strip())
                                last_output_time = time.time()
                            else:
                                # Send periodic heartbeat to show process is still alive
                                current_time = time.time()
                                time_since_last_output = current_time - last_output_time
                                
                                # Send heartbeat every 30 seconds
                                if int(time_since_last_output) % 30 == 0 and int(time_since_last_output) > 0:
                                    output_queue.put(f"⏳ Scenario creation in progress... (no output for {int(time_since_last_output)} seconds)")
                                
                                # Check for timeout
                                if time_since_last_output > timeout_seconds:
                                    output_queue.put(f"⚠️ Warning: No output for {timeout_seconds} seconds, process may be stuck")
                                    output_queue.put(f"🔧 Debug: Terminating process due to timeout")
                                    process.terminate()
                                    try:
                                        process.wait(timeout=10)
                                    except subprocess.TimeoutExpired:
                                        process.kill()
                                        process.wait()
                                    output_queue.put("__SCENARIO_ERROR__: Process terminated due to timeout (no output for 10 minutes)")
                                    return
                                    
                    except Exception as read_error:
                        output_queue.put(f"🔧 Debug: Error reading output: {read_error}")
                    
                    # Wait for process to complete
                    return_code = process.wait()
                    output_queue.put(f"🔧 Debug: Process completed with return code {return_code}")
                    
                    # Signal completion
                    if return_code == 0:
                        # Load the created inputs to send back to frontend
                        try:
                            inputs_file = Path(__file__).parent / 'inputs.json'
                            with open(inputs_file, 'r', encoding='utf-8') as f:
                                current_inputs = json.load(f)
                            
                            scenario_inputs = current_inputs.get(scenario_name, {})
                            output_queue.put(f"__SCENARIO_COMPLETE__:{json.dumps(scenario_inputs)}")
                        except Exception as e:
                            output_queue.put(f"__SCENARIO_COMPLETE__:{{}}")
                    else:
                        output_queue.put(f"__SCENARIO_ERROR__: Process exited with code {return_code}")
                        
                finally:
                    # Clean up temporary script file
                    try:
                        if script_path.exists():
                            script_path.unlink()
                            output_queue.put(f"🔧 Debug: Cleaned up temporary script")
                    except Exception as cleanup_error:
                        output_queue.put(f"⚠️ Warning: Could not clean up temporary script: {cleanup_error}")
                        
            except Exception as e:
                output_queue.put(f"__SCENARIO_ERROR__: {str(e)}")
                output_queue.put(f"🔧 Debug: Exception in run_scenario_creation: {e}")
            finally:
                # Clean up
                if session_id in analysis_processes:
                    del analysis_processes[session_id]
                output_queue.put("Session cleanup completed")
        
        # Start scenario creation in background thread
        thread = threading.Thread(target=run_scenario_creation, name=f"create-scenario-{session_id}")
        thread.daemon = False
        thread.start()
        
        # Store thread reference for cleanup
        analysis_processes[f"{session_id}_thread"] = thread
        
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "message": f"Scenario creation started for '{scenario_name}' with liveboard: {liveboard_id}"
        })
        
    except Exception as e:
        print(f"❌ Error starting scenario creation: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/create-scenario-progress/<session_id>')
def get_create_scenario_progress(session_id):
    """Stream scenario creation progress for a session"""
    def generate():
        if session_id not in analysis_outputs:
            yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"
            return
            
        output_queue = analysis_outputs[session_id]
        
        try:
            while True:
                try:
                    # Get message from queue with timeout
                    message = output_queue.get(timeout=1)
                    
                    if message.startswith("__SCENARIO_COMPLETE__:"):
                        inputs_data_json = message.replace("__SCENARIO_COMPLETE__:", "")
                        try:
                            inputs_data = json.loads(inputs_data_json)
                        except:
                            inputs_data = {}
                        yield f"data: {json.dumps({'complete': True, 'message': 'Scenario creation completed successfully', 'inputs_data': inputs_data})}\n\n"
                        break
                    elif message.startswith("__SCENARIO_ERROR__"):
                        error_msg = message.replace("__SCENARIO_ERROR__: ", "")
                        yield f"data: {json.dumps({'error': True, 'message': error_msg})}\n\n"
                        break
                    else:
                        yield f"data: {json.dumps({'output': message})}\n\n"
                        
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                    continue
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': True, 'message': f'Stream error: {str(e)}'})}\n\n"
        finally:
            # Clean up
            if session_id in analysis_outputs:
                del analysis_outputs[session_id]
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/config.js', methods=['GET'])
def serve_config_js():
    """Serve config.js file with backend configuration"""
    backend_port = os.getenv('PORT', '5005')
    
    config_js_content = f"""// Auto-generated backend configuration
window.BACKEND_CONFIG = {{
    port: '{backend_port}',
    url: 'http://localhost:{backend_port}',
    version: '1.0.0',
    generated_at: '{datetime.now().isoformat()}'
}};

console.log('✅ Backend config loaded:', window.BACKEND_CONFIG);
"""
    
    response = Response(config_js_content, mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache' 
    response.headers['Expires'] = '0'
    return response


# Serve frontend files
@app.route('/')
def serve_index():
    """Serve the main frontend page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files (JS, CSS, etc.)"""
    try:
        return send_from_directory('../frontend', path)
    except:
        # If file not found, return 404
        return "File not found", 404


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get backend configuration from .env file for frontend"""
    backend_port = os.getenv('PORT', '5005')
    return jsonify({
        "backend_port": backend_port,
        "backend_url": f"http://localhost:{backend_port}"
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API server is running"})

@app.route('/api/settings/env', methods=['GET', 'POST'])
def manage_env_settings():
    """Get or update .env file settings"""
    env_file_path = Path(__file__).parent / '.env'
    
    if request.method == 'GET':
        # Return current settings (masked for security)
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file_path)
            
            # Get current values and mask them for security
            current_settings = {}
            
            ts_url = os.getenv('THOUGHTSPOT_BASE_URL', '')
            ts_token = os.getenv('THOUGHTSPOT_AUTH_TOKEN', '')
            claude_key = os.getenv('CLAUDE_API_KEY', '')
            openai_key = os.getenv('OPENAI_API_KEY', '')
            gemini_key = os.getenv('GEMINI_API_KEY', '')
            llm_provider = os.getenv('LLM_PROVIDER', 'claude')
            port = os.getenv('PORT', '5005')
            
            current_settings['thoughtspot_base_url'] = ts_url if ts_url else ''
            current_settings['thoughtspot_auth_token'] = '***' + ts_token[-4:] if len(ts_token) > 4 else ('Set' if ts_token else 'Not set')
            current_settings['claude_api_key'] = '***' + claude_key[-4:] if len(claude_key) > 4 else ('Set' if claude_key else 'Not set')
            current_settings['openai_api_key'] = '***' + openai_key[-4:] if len(openai_key) > 4 else ('Set' if openai_key else 'Not set')
            current_settings['gemini_api_key'] = '***' + gemini_key[-4:] if len(gemini_key) > 4 else ('Set' if gemini_key else 'Not set')
            current_settings['llm_provider'] = llm_provider
            current_settings['port'] = port
            
            return jsonify({
                "success": True,
                "settings": current_settings
            })
            
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to read settings: {str(e)}"
            })
    
    elif request.method == 'POST':
        # Update .env file with new settings
        try:
            data = request.get_json()
            
            # Validate required data
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No data provided"
                })
            
            # Get new values
            new_ts_url = data.get('thoughtspot_base_url', '').strip()
            new_ts_token = data.get('thoughtspot_auth_token', '').strip()
            new_claude_key = data.get('claude_api_key', '').strip()
            new_openai_key = data.get('openai_api_key', '').strip()
            new_gemini_key = data.get('gemini_api_key', '').strip()
            new_llm_provider = data.get('llm_provider', '').strip()
            new_port = data.get('port', '').strip()
            
            print(f"🔍 Received data: llm_provider='{new_llm_provider}'")
            
            # Validate LLM provider if provided
            if new_llm_provider and new_llm_provider not in ['claude', 'openai', 'gemini']:
                return jsonify({
                    "success": False,
                    "error": "LLM provider must be one of: claude, openai, gemini"
                })
            
            # Validate port number if provided
            if new_port and not (new_port.isdigit() and 1 <= int(new_port) <= 65535):
                return jsonify({
                    "success": False,
                    "error": "Port must be a number between 1 and 65535"
                })
            
            # Validate that at least one field is provided
            if not any([new_ts_url, new_ts_token, new_claude_key, new_openai_key, new_gemini_key, new_llm_provider, new_port]):
                return jsonify({
                    "success": False,
                    "error": "At least one setting must be provided"
                })
            
            # Read existing .env file
            env_vars = {}
            if env_file_path.exists():
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
            
            # Update with new values (only if provided)
            if new_ts_url:
                env_vars['THOUGHTSPOT_BASE_URL'] = new_ts_url
            if new_ts_token:
                env_vars['THOUGHTSPOT_AUTH_TOKEN'] = new_ts_token
            if new_claude_key:
                env_vars['CLAUDE_API_KEY'] = new_claude_key
            if new_openai_key:
                env_vars['OPENAI_API_KEY'] = new_openai_key
            if new_gemini_key:
                env_vars['GEMINI_API_KEY'] = new_gemini_key
            if new_llm_provider:
                print(f"✏️ Updating LLM_PROVIDER from '{env_vars.get('LLM_PROVIDER', 'not set')}' to '{new_llm_provider}'")
                env_vars['LLM_PROVIDER'] = new_llm_provider
            if new_port:
                env_vars['PORT'] = new_port
            
            # Write updated .env file
            with open(env_file_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            print(f"✅ Updated .env file with new settings")
            print(f"🔧 Updated fields: {[k for k, v in {'THOUGHTSPOT_BASE_URL': new_ts_url, 'THOUGHTSPOT_AUTH_TOKEN': new_ts_token, 'CLAUDE_API_KEY': new_claude_key, 'OPENAI_API_KEY': new_openai_key, 'GEMINI_API_KEY': new_gemini_key, 'LLM_PROVIDER': new_llm_provider, 'PORT': new_port}.items() if v]}")
            
            # Reload environment variables
            from dotenv import load_dotenv
            load_dotenv(env_file_path, override=True)
            
            return jsonify({
                "success": True,
                "message": "Settings updated successfully",
                "updated_fields": [k for k, v in {
                    'THOUGHTSPOT_BASE_URL': new_ts_url, 
                    'THOUGHTSPOT_AUTH_TOKEN': new_ts_token, 
                    'CLAUDE_API_KEY': new_claude_key,
                    'OPENAI_API_KEY': new_openai_key,
                    'GEMINI_API_KEY': new_gemini_key,
                    'LLM_PROVIDER': new_llm_provider,
                    'PORT': new_port
                }.items() if v]
            })
            
        except Exception as e:
            print(f"❌ Error updating .env file: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to update settings: {str(e)}"
            })


@app.route('/api/settings/test', methods=['POST'])
def test_api_connections():
    """Test API connections with current or provided credentials"""
    try:
        data = request.get_json() or {}
        
        # Get credentials from request or environment
        ts_url = data.get('thoughtspot_base_url') or os.getenv('THOUGHTSPOT_BASE_URL')
        ts_token = data.get('thoughtspot_auth_token') or os.getenv('THOUGHTSPOT_AUTH_TOKEN')
        claude_key = data.get('claude_api_key') or os.getenv('CLAUDE_API_KEY')
        openai_key = data.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        gemini_key = data.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
        
        results = {}
        
        # Test ThoughtSpot connection
        if ts_url and ts_token:
            try:
                import requests
                headers = {
                    'Authorization': f'Bearer {ts_token}',
                    'Content-Type': 'application/json'
                }
                # Simple API call to test connection
                response = requests.get(f"{ts_url.rstrip('/')}/api/rest/2.0/system/health", 
                                      headers=headers, timeout=10)
                if response.status_code == 200:
                    results['thoughtspot'] = {'status': 'success', 'message': 'Connection successful'}
                else:
                    results['thoughtspot'] = {'status': 'error', 'message': f'HTTP {response.status_code}'}
            except Exception as e:
                results['thoughtspot'] = {'status': 'error', 'message': f'Connection failed: {str(e)}'}
        else:
            results['thoughtspot'] = {'status': 'error', 'message': 'URL or token not configured'}
        
        # Test Claude connection
        if claude_key:
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=claude_key)
                # Simple test message
                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                results['claude'] = {'status': 'success', 'message': 'API key valid'}
            except Exception as e:
                results['claude'] = {'status': 'error', 'message': f'Authentication failed: {str(e)}'}
        else:
            results['claude'] = {'status': 'error', 'message': 'API key not configured'}
        
        # Test OpenAI connection
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                # Simple test message
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                results['openai'] = {'status': 'success', 'message': 'API key valid'}
            except Exception as e:
                results['openai'] = {'status': 'error', 'message': f'Authentication failed: {str(e)}'}
        else:
            results['openai'] = {'status': 'error', 'message': 'API key not configured'}
        
        # Test Gemini connection
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                # Simple test message
                response = model.generate_content("Hi")
                results['gemini'] = {'status': 'success', 'message': 'API key valid'}
            except Exception as e:
                results['gemini'] = {'status': 'error', 'message': f'Authentication failed: {str(e)}'}
        else:
            results['gemini'] = {'status': 'error', 'message': 'API key not configured'}
        
        return jsonify({
            "success": True,
            "tests": results
        })
        
    except Exception as e:
        print(f"❌ Error testing connections: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to test connections: {str(e)}"
        })


if __name__ == '__main__':
    print("🚀 Starting AI Hybrid Analysis Platform Server...")
    print(f"📁 Inputs file: {INPUTS_FILE}")
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5005))
    
    print(f"🌐 Server running on: http://localhost:{port}")
    print(f"🎨 Frontend UI: http://localhost:{port}")
    print(f"🔧 API Base: http://localhost:{port}/api/")
    print("📋 Available endpoints:")
    print("  GET  / - Frontend application")
    print("  GET  /config.js - Auto-generated configuration")
    print("  GET  /api/config - Get backend configuration")
    print("  GET  /api/inputs - Get current inputs")
    print("  POST /api/inputs - Update all inputs")
    print("  POST /api/inputs/scenario - Update specific scenario")
    print("  POST /api/create-scenario - Create new scenario")
    print("  POST /api/populate-inputs - Auto-populate inputs")
    print("  POST /api/analysis/start - Start analysis")
    print("  GET  /api/analysis/progress/<session_id> - Get analysis progress")
    print("  GET  /api/scenarios - Get available scenarios")
    print("  GET  /api/versions/<scenario> - Get scenario versions")
    print("  GET  /api/report/<scenario>/<version> - Get report content")
    print("  GET  /api/settings/env - Get environment settings")
    print("  POST /api/settings/env - Update environment settings")
    print("  POST /api/settings/test - Test API connections")
    print("  GET  /api/health - Health check")
    print()
    print("💡 Open your browser and go to the URL above to access the application")
    print("⚙️ Use the Settings tab to configure API keys and ports")
    
    app.run(host='0.0.0.0', port=port, debug=True)
