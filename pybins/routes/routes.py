import os
from flask import send_from_directory
from flask import Blueprint, request, jsonify, abort, Response
from ..worker.tasks import build_package_task, run_build, get_build_status, list_builds
from ..fetcher.fetcher import fetch_from_pypi, fetch_from_github
from ..storage.storage import PackageStorage


routes_bp = Blueprint('routes', __name__)

# download endpoint for build artifacts and logs
@routes_bp.route('/download/<build_id>/<filename>', methods=['GET'])
def download_artifact(build_id, filename):
    """Serve build artifacts and logs from the artifacts directory."""
    ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../artifacts'))
    build_dir = os.path.join(ARTIFACTS_DIR, build_id)
    if not os.path.exists(os.path.join(build_dir, filename)):
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory(build_dir, filename, as_attachment=True)



storage = PackageStorage()

@routes_bp.route('/', methods=['GET'])
def index():
    """Home page with API information"""
    return jsonify({
        'service': 'PyBins - Python Package Freezer',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'This help message',
            'POST /enqueue': 'Enqueue a package build',
            'POST /build': 'Build a package',
            'GET /build/<build_id>': 'Get build status',
            'GET /builds': 'List all builds',
            'GET /packages': 'List all packages',
            'POST /packages': 'Add a package',
            'GET /<tool>': 'Get installer script for tool',
            'GET /<tool>@<version>': 'Get installer script for specific version',
            'GET /meta/<tool>': 'Get package metadata',
            'GET /health': 'Health check'
        }
    })

@routes_bp.route('/enqueue', methods=['POST'])
def enqueue_build():
    """Enqueue a package build"""
    data = request.get_json()
    if not data or 'package' not in data:
        return jsonify({'error': 'Package name is required'}), 400
    
    package_name = data['package']
    version = data.get('version', 'latest')
    
   
    result = build_package_task(package_name, version)
    
    return jsonify({
        'message': 'Build enqueued successfully',
        'build_id': result['build_id'],
        'status': result['status']
    }), 202

@routes_bp.route('/build', methods=['POST'])
def build_package():
    """Build a package immediately"""
    data = request.get_json()
    if not data or 'package' not in data:
        return jsonify({'error': 'Package name is required'}), 400
    
    package_name = data['package']
    version = data.get('version', 'latest')
    build_type = data.get('build_type', 'wheel')
    
    result = run_build(package_name, version, build_type)
    
    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@routes_bp.route('/build/<build_id>', methods=['GET'])
def get_build_info(build_id):
    """Get build status and information"""
    build_info = get_build_status(build_id)
    if not build_info:
        return jsonify({'error': 'Build not found'}), 404
    
    return jsonify(build_info)

@routes_bp.route('/builds', methods=['GET'])
def get_all_builds():
    """List all builds"""
    builds = list_builds()
    return jsonify({
        'builds': builds,
        'count': len(builds)
    })

@routes_bp.route('/packages', methods=['GET'])
def get_packages():
    """List all registered packages"""
    packages = storage.get_packages()
    return jsonify({
        'packages': packages,
        'count': len(packages)
    })

@routes_bp.route('/packages', methods=['POST'])
def add_package():
    """Add a new package"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Package name is required'}), 400
    
    name = data['name']
    version = data.get('version', 'latest')
    source_url = data.get('source_url', '')
    
    package_id = storage.add_package(name, version, source_url)
    
    return jsonify({
        'message': 'Package added successfully',
        'package_id': package_id,
        'name': name,
        'version': version
    }), 201

@routes_bp.route('/<path:tool_request>', methods=['GET'])
def get_installer(tool_request):
    """
    Handles both:
    - /tool
    - /tool@version
    """
    if '@' in tool_request:
        tool, version = tool_request.split('@', 1)
    else:
        tool, version = tool_request, None

    user_agent = request.headers.get('User-Agent', '').lower()

    # Detect OS
    if 'windows' in user_agent:
        os_type = 'windows'
    elif 'linux' in user_agent:
        os_type = 'linux'
    elif 'darwin' in user_agent or 'mac os' in user_agent:
        os_type = 'macos'
    else:
        os_type = 'linux'  # Default to linux instead of aborting

    # Detect Arch
    if 'x86_64' in user_agent or 'amd64' in user_agent:
        arch = 'x86_64'
    elif 'arm64' in user_agent or 'aarch64' in user_agent:
        arch = 'arm64'
    else:
        arch = 'x86_64'  # Default architecture

    # Fetch package info
    package_info = fetch_from_pypi(tool, version)
    if not package_info:
        abort(404, description="Tool or version not found")

    installer_script = package_info.get('installer_script')
    if not installer_script:
        # Generate basic installer script
        version_spec = f"=={version}" if version else ""
        installer_script = f'''#!/bin/bash
# Installer for {tool}{version_spec}
echo "Installing {tool}..."
pip install {tool}{version_spec}
echo "Installation complete!"
'''

    return Response(installer_script, mimetype='text/x-sh')

@routes_bp.route('/meta/<tool>', methods=['GET'])
def get_tool_meta(tool):
    """Get package metadata"""
    metadata = fetch_from_pypi(tool)
    if not metadata:
        abort(404, description="Tool not found")
    
    return jsonify({
        'name': metadata.get('name', tool),
        'version': metadata.get('version', 'unknown'),
        'author': metadata.get('author', 'Unknown'),
        'description': metadata.get('description', 'No description available'),
        'package_url': metadata.get('package_url', '')
    })

@routes_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'pybins',
        'timestamp': storage.builds.__len__() if hasattr(storage, 'builds') else 0
    })
