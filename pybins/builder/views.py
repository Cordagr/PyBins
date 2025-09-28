from flask import Flask, request, jsonify
from ..worker.tasks import build_package_task

app = Flask(__name__)

@app.route('/build_binary/<pkg>', methods=['POST'])
def build_binary(pkg):
    package_id = pkg
    version = request.form.get('version', 'latest')
    task = build_package_task.delay(package_id, version)
    return jsonify({"task_id": task.id}), 202
