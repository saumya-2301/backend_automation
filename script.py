import os
import platform
import subprocess
import google.generativeai as genai
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# Set up Gemini API Key (Replace with your actual key)
genai.configure(api_key="your_gemini_api_key")

# Function to fetch OS details
def get_system_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture()[0]
    }

# Function to generate shell script using Gemini AI
def generate_script(command):
    system_info = get_system_info()
    
    prompt = f"""
    You are an AI that converts natural language requests into shell scripts.
    - User Command: {command}
    - System Info: {system_info}
    - Generate a shell script to execute the requested task.
    Only output the script, without any explanation.
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    return response.text.strip()

# Function to execute the generated script
def execute_script(script, os_type):
    try:
        if os_type == "Windows":
            process = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, shell=True)
        else:
            process = subprocess.run(["bash", "-c", script], capture_output=True, text=True, shell=True)

        return process.stdout if process.returncode == 0 else process.stderr
    except Exception as e:
        return str(e)

# API Endpoint for Automation
@app.route("/automate", methods=["POST"])
def automate_process():
    data = request.get_json()
    user_command = data.get("command", "")

    if not user_command:
        return jsonify({"error": "No command provided"}), 400

    system_info = get_system_info()
    script = generate_script(user_command)
    execution_output = execute_script(script, system_info["os"])

    return jsonify({
        "command": user_command,
        "system_info": system_info,
        "generated_script": script,
        "execution_output": execution_output
    })

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
