import os
from flask import Flask, request, jsonify
import paramiko
from scp import SCPClient

app = Flask(__name__)

# --- Configuration ---
PREDEFINED_TOKEN = os.getenv("SAM_PROXY_TOKEN")
REMOTE_HOST = os.getenv("SAMH_HOST")
REMOTE_USER = os.getenv("SAMH_USER")
PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa") # Path to your private key
REMOTE_DEST_PATH = "~/data"

def send_file_via_scp(local_path, remote_filename):
    """Handles the SSH connection using a Private Key and SCP transfer."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Load the private key
        # Use paramiko.Ed25519Key.from_private_key_file if using an Ed25519 key
        k = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)
        
        # Connect using the key
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, pkey=k)
        
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_path, os.path.join(REMOTE_DEST_PATH, remote_filename))
        
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        ssh.close()

@app.route('/upload', methods=['POST'])
def upload_parquet():
    # Token Validation
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {PREDEFINED_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.parquet'):
        return jsonify({"error": "Only .parquet files allowed"}), 400

    # Save temporarily
    temp_path = os.path.join("/tmp", file.filename)
    file.save(temp_path)

    # SCP Transfer
    success, message = send_file_via_scp(temp_path, file.filename)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

    if success:
        return jsonify({"status": "Transfer complete"}), 200
    return jsonify({"error": message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
