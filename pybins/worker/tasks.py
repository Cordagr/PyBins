# Package building tasks for Flask

import subprocess
import os
import tempfile
from datetime import datetime
from ..storage.storage import PackageStorage
from ..storage.models import PackageWheel

# Initialize storage
storage = PackageStorage()

def build_package_task(package_name, version):
    """Download, build, and store a Python package wheel. Returns build info and download link."""
    from ..fetcher.fetcher import fetch_from_pypi, download_package
    ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../artifacts'))
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    build_id = f"{package_name}-{version}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    result = {
        'build_id': build_id,
        'package_name': package_name,
        'version': version,
        'status': 'pending',
        'started_at': datetime.now().isoformat()
    }
    storage.builds[build_id] = result
    try:
        result['status'] = 'in_progress'
        # 1. Fetch package info from PyPI
        pkg_info = fetch_from_pypi(package_name, version if version != 'latest' else None)
        if not pkg_info or not pkg_info.get('url'):
            raise Exception(f"Could not find package {package_name} version {version}")
        # 2. Download the source distribution
        src_path = download_package(pkg_info['url'], ARTIFACTS_DIR)
        if not src_path:
            raise Exception("Failed to download package source.")
        # 3. Extract and build wheel
        import tarfile, zipfile
        extract_dir = os.path.join(ARTIFACTS_DIR, f"{build_id}_src")
        os.makedirs(extract_dir, exist_ok=True)
        if src_path.endswith('.tar.gz') or src_path.endswith('.tgz'):
            with tarfile.open(src_path, 'r:gz') as tar:
                tar.extractall(path=extract_dir)
        elif src_path.endswith('.zip'):
            with zipfile.ZipFile(src_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        else:
            raise Exception("Unknown source archive format.")
        # 4. Find the directory with setup.py or pyproject.toml
        build_root = extract_dir
        for root, dirs, files in os.walk(extract_dir):
            if 'setup.py' in files or 'pyproject.toml' in files:
                build_root = root
                break
        # 5. Build wheel using 'python -m build --wheel'
        wheel_dir = os.path.join(ARTIFACTS_DIR, build_id)
        os.makedirs(wheel_dir, exist_ok=True)
        log_path = os.path.join(wheel_dir, 'build.log')
        try:
            with open(log_path, 'w') as logf:
                proc = subprocess.run([
                    'python', '-m', 'build', '--wheel', '--outdir', wheel_dir
                ], cwd=build_root, stdout=logf, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError:
            result['status'] = 'failed'
            result['finished_at'] = datetime.now().isoformat()
            result['output'] = f"Build failed. See log at /download/{build_id}/build.log"
            result['download_url'] = f"/download/{build_id}/build.log"
            return result
        # 6. Find the built wheel
        wheel_files = [f for f in os.listdir(wheel_dir) if f.endswith('.whl')]
        if not wheel_files:
            raise Exception("Wheel build failed: no .whl file found.")
        wheel_file = wheel_files[0]
        wheel_path = os.path.join(wheel_dir, wheel_file)
        result['status'] = 'success'
        result['finished_at'] = datetime.now().isoformat()
        result['output'] = f"Successfully built {package_name} version {version}"
        result['download_url'] = f"/download/{build_id}/{wheel_file}"
        result['log_url'] = f"/download/{build_id}/build.log"
        return result
    except Exception as e:
        result['status'] = 'failed'
        result['finished_at'] = datetime.now().isoformat()
        result['output'] = str(e)
        return result

def run_build(package_name, version, build_type="wheel"):
    """Run a build process (wheel or binary)."""
    if build_type == "wheel":
        return build_package_task(package_name, version)
    elif build_type == "binary":
        return build_binary_task(package_name, version)
    else:
        return {'success': False, 'error': f"Unknown build type: {build_type}"}

def build_binary_task(package_name, version):
    """Download, build, and store a Python package binary using pyinstaller."""
    from ..fetcher.fetcher import fetch_from_pypi, download_package
    ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../artifacts'))
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    build_id = f"{package_name}-{version}-bin-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    result = {
        'build_id': build_id,
        'package_name': package_name,
        'version': version,
        'status': 'pending',
        'started_at': datetime.now().isoformat()
    }
    storage.builds[build_id] = result
    try:
        result['status'] = 'in_progress'
        # 1. Fetch package info from PyPI
        pkg_info = fetch_from_pypi(package_name, version if version != 'latest' else None)
        if not pkg_info or not pkg_info.get('url'):
            raise Exception(f"Could not find package {package_name} version {version}")
        # 2. Download the source distribution
        src_path = download_package(pkg_info['url'], ARTIFACTS_DIR)
        if not src_path:
            raise Exception("Failed to download package source.")
        # 3. Extract source
        import tarfile, zipfile
        extract_dir = os.path.join(ARTIFACTS_DIR, f"{build_id}_src")
        os.makedirs(extract_dir, exist_ok=True)
        if src_path.endswith('.tar.gz') or src_path.endswith('.tgz'):
            with tarfile.open(src_path, 'r:gz') as tar:
                tar.extractall(path=extract_dir)
        elif src_path.endswith('.zip'):
            with zipfile.ZipFile(src_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        else:
            raise Exception("Unknown source archive format.")
        # 4. Find the main script (try __main__.py or setup.py entry point)
        main_script = None
        for root, dirs, files in os.walk(extract_dir):
            if '__main__.py' in files:
                main_script = os.path.join(root, '__main__.py')
                break
        if not main_script:
            # Fallback: look for a .py file matching the package name
            for root, dirs, files in os.walk(extract_dir):
                for f in files:
                    if f == f'{package_name}.py':
                        main_script = os.path.join(root, f)
                        break
        if not main_script:
            raise Exception("Could not find an entry script (__main__.py or <package>.py) for binary build.")
        # 5. Build binary using pyinstaller
        bin_dir = os.path.join(ARTIFACTS_DIR, build_id)
        os.makedirs(bin_dir, exist_ok=True)
        log_path = os.path.join(bin_dir, 'build.log')
        try:
            with open(log_path, 'w') as logf:
                proc = subprocess.run([
                    'pyinstaller', '--onefile', '--distpath', bin_dir, main_script
                ], cwd=os.path.dirname(main_script), stdout=logf, stderr=subprocess.STDOUT, check=True)
        except subprocess.CalledProcessError:
            result['status'] = 'failed'
            result['finished_at'] = datetime.now().isoformat()
            result['output'] = f"Binary build failed. See log at /download/{build_id}/build.log"
            result['download_url'] = f"/download/{build_id}/build.log"
            return result
        # 6. Find the built binary
        bin_files = [f for f in os.listdir(bin_dir) if os.path.isfile(os.path.join(bin_dir, f)) and f != 'build.log']
        if not bin_files:
            raise Exception("Binary build failed: no binary file found.")
        bin_file = bin_files[0]
        bin_path = os.path.join(bin_dir, bin_file)
        result['status'] = 'success'
        result['finished_at'] = datetime.now().isoformat()
        result['output'] = f"Successfully built binary for {package_name} version {version}"
        result['download_url'] = f"/download/{build_id}/{bin_file}"
        result['log_url'] = f"/download/{build_id}/build.log"
        return result
    except Exception as e:
        result['status'] = 'failed'
        result['finished_at'] = datetime.now().isoformat()
        result['output'] = str(e)
        return result
def get_build_status(build_id):
    """Get the status of a build"""
    return storage.builds.get(build_id, None)

def list_builds():
    """List all builds"""
    return list(storage.builds.values())
