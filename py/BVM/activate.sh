#!/bin/bash
# BVM 虛擬環境啟動腳本

# 啟動虛擬環境
source venv/bin/activate

echo "=========================================="
echo "BVM Virtual Environment Activated"
echo "=========================================="
echo ""
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""
echo "已安裝的套件:"
pip list | grep -E "(requests|PyYAML|ruamel)"
echo ""
echo "使用方式:"
echo "  python bvm_config.py          # 測試配置"
echo "  python example_usage.py       # 查看範例"
echo "  python bvm_client.py          # 測試客戶端"
echo ""
echo "離開虛擬環境: deactivate"
echo "=========================================="
