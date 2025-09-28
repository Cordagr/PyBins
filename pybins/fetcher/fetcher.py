# Pull Packages from PyPI/GitHub
import requests
from packaging import version
import subprocess
import os
import shutil

def fetch_from_pypi(tool, version=None):
    """Fetch package info from PyPI"""
    url = f"https://pypi.org/pypi/{tool}/json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        
        if version:
            releases = data.get('releases', {})
            if version in releases and releases[version]:
                return {
                    'name': tool,
                    'version': version,
                    'url': releases[version][-1]['url'],
                    'author': data['info'].get('author', 'Unknown'),
                    'description': data['info'].get('summary', 'No description'),
                    'package_url': data['info'].get('package_url', '')
                }
        else:
            # Return latest version info
            latest_version = data['info']['version']
            releases = data.get('releases', {})
            if latest_version in releases and releases[latest_version]:
                return {
                    'name': tool,
                    'version': latest_version,
                    'url': releases[latest_version][-1]['url'],
                    'author': data['info'].get('author', 'Unknown'),
                    'description': data['info'].get('summary', 'No description'),
                    'package_url': data['info'].get('package_url', ''),
                    'installer_script': generate_installer_script(tool, latest_version)
                }
        return None
    except Exception as e:
        print(f"Error fetching from PyPI: {e}")
        return None

def fetch_from_github(repo, version=None):
    """Fetch package info from GitHub releases"""
    api_url = f"https://api.github.com/repos/{repo}/releases"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return None
        releases = response.json()
        if not releases:
            return None
            
        if version:
            for release in releases:
                if release['tag_name'] == version:
                    return {
                        'name': repo.split('/')[-1],
                        'version': version,
                        'url': release['tarball_url'],
                        'description': release.get('body', 'No description')
                    }
            return None
        else:
            latest_release = releases[0]
            return {
                'name': repo.split('/')[-1],
                'version': latest_release['tag_name'],
                'url': latest_release['tarball_url'],
                'description': latest_release.get('body', 'No description')
            }
    except Exception as e:
        print(f"Error fetching from GitHub: {e}")
        return None

def download_package(url, dest_folder):
    """Download package from URL"""
    try:
        local_filename = url.split('/')[-1]
        local_path = os.path.join(dest_folder, local_filename)
        
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return local_path
    except Exception as e:
        print(f"Error downloading package: {e}")
        return None

def generate_installer_script(tool, version):
    """Generate installation script for a tool"""
    return f'''#!/bin/bash
        # Auto-generated installer for {tool} v{version}
        echo "Installing {tool} version {version}..."
        pip install {tool}=={version}
        echo "Installation complete!"
        '''


