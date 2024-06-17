from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import threading
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)

processes = defaultdict(dict)
outputs = defaultdict(lambda: defaultdict(str))

def start_process(command, name, session_id):
    try:
        if name in processes[session_id] and processes[session_id][name].poll() is None:
            processes[session_id][name].terminate()
            processes[session_id][name].wait()
            outputs[session_id][name] += f"{name} script stopped\n"
        process = subprocess.Popen(
            ["python", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes[session_id][name] = process
        outputs[session_id][name] += f"{name} script started\n"
        threading.Thread(target=read_output, args=(process, name, session_id)).start()
    except Exception as e:
        outputs[session_id][name] += f"Error starting {name} script: {str(e)}\n"

def read_output(process, name, session_id):
    try:
        for line in iter(process.stdout.readline, ''):
            outputs[session_id][name] += f"{name}: {line}"
        process.stdout.close()
    except Exception as e:
        outputs[session_id][name] += f"Error reading output from {name} script: {str(e)}\n"
    finally:
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()

@app.route('/start', methods=['POST'])
def start_script():
    data = request.json
    script_name = data.get('name')
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    if script_name in ["DESP", "OA", "PO", "BS", "AM"]:
        script_paths = {
            "DESP": "N:/REPORTING/Test folder/Parsing/Despatch and invoice/PDFs.py",
            "OA": "N:/REPORTING/Test folder/Parsing/Acknowledgement/PDFs.py",
            "PO": "N:/REPORTING/Test folder/Parsing/POs/PDFs.py",
            "BS": "N:/REPORTING/Test folder/Parsing/BS/AUTObsPARSE.py",
            "AM": "N:/REPORTING/Test folder/Parsing/AM/AUTOamPARSE.py"
        }
        start_process(script_paths[script_name], script_name, session_id)
        return jsonify({"message": f"{script_name} script started"}), 200
    return jsonify({"error": "Invalid script name"}), 400

@app.route('/stop', methods=['POST'])
def stop_script():
    data = request.json
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    for name, process in processes[session_id].items():
        try:
            if process and process.poll() is None:
                process.terminate()
                outputs[session_id][name] += f"{name} script stopped\n"
        except Exception as e:
            outputs[session_id][name] += f"Error stopping {name} script: {str(e)}\n"
    return jsonify({"message": "All scripts stopped"}), 200

@app.route('/output', methods=['GET'])
def get_output():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    return jsonify(outputs[session_id])

@app.route('/export', methods=['GET'])
def export_output():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({"error": "session_id is required"}), 400
        if not os.path.exists("Output"):
            os.makedirs("Output")
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
        filename = f"Output/output_{timestamp}.txt"
        with open(filename, "w") as file:
            for output in outputs[session_id].values():
                file.write(output)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
