from flask import Blueprint, jsonify, request
from .tasks import build_package_task, run_build, get_build_status, list_builds

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/builds', methods=['GET'])
def get_builds():
    """Get all builds"""
    builds = list_builds()
    return jsonify({
        'builds': builds,
        'count': len(builds)
    })

@worker_bp.route('/builds/<build_id>', methods=['GET'])
def get_build(build_id):
    """Get specific build by ID"""
    build = get_build_status(build_id)
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    return jsonify(build)

@worker_bp.route('/builds', methods=['POST'])
def create_build():
    """Create a new build"""
    data = request.get_json()
    if not data or 'package' not in data:
        return jsonify({'error': 'Package name is required'}), 400
    
    package_name = data['package']
    version = data.get('version', 'latest')
    
    result = build_package_task(package_name, version)
    
    return jsonify({
        'message': 'Build created successfully',
        'build': result
    }), 201

@worker_bp.route('/builds/<build_id>/status', methods=['GET'])
def get_build_status_route(build_id):
    """Get build status"""
    build = get_build_status(build_id)
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    
    return jsonify({
        'build_id': build_id,
        'status': build.get('status', 'unknown'),
        'package_name': build.get('package_name'),
        'version': build.get('version')
    })

@worker_bp.route('/run', methods=['POST'])
def run_build_now():
    """Run a build immediately"""
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
