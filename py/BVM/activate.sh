#!/bin/bash
# BVM Virtual Environment Activation Script

# Activate virtual environment
source venv/bin/activate

echo "=========================================="
echo "BVM Virtual Environment Activated"
echo "=========================================="
echo ""
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""
echo "Installed packages:"
pip list | grep -E "(requests|PyYAML|ruamel)"
echo ""
echo "Usage:"
echo "  python bvm_config.py          # Test configuration"
echo "  python example_usage.py       # View examples"
echo "  python bvm_client.py          # Test client"
echo ""
echo "Exit virtual environment: deactivate"
echo "=========================================="
