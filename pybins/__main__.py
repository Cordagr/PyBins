#!/usr/bin/env python3
"""
Entry point for running the pybins package as a module.
This allows the package to be executed with: python -m pybins
"""

from . import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)