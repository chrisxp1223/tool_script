#!/usr/bin/env python3
"""Fix translation issues"""

import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix mixed translations
    fixes = [
        # Common patterns
        ("共享Basic類別", "Shared Base Class"),
        ("客戶端Basic類別", "BVM API Client Base Class"),
        ("Provides common functionality for all BVM tools：", "Provides common functionality for all BVM tools:"),
        ("Authentication與 token 管理", "Authentication and token management"),
        ("Base BIOS 處理", "Base BIOS handling"),
        ("Logging Configuration", "Logging configuration"),
        ("# ==================== Constants ====================", "# ==================== Constants ===================="),
        ("If using config，可省略", "Optional if using config"),
        ("預設:", "Default:"),
        ("Optional)", "Optional)"),
        ("使用方式:", "Usage:"),
        ("方式 1:", "Method 1:"),
        ("方式 2:", "Method 2:"),
        ("方式 3:", "Method 3:"),
        ("直接傳入Authentication資訊", "Direct credentials"),
        ("使用Configuration檔案", "Using config file"),
        ("實例", "instance"),
        ("ConfigurationFile paths", "Configuration file path"),
        ("載入Configuration", "Load configuration"),
        ("SetAuthentication資訊", "Set authentication info"),
        ("自動登入", "Auto login"),
        ("登入 BVM 並Get token", "Login to BVM and get token"),
        ("Get帶 token 的Authentication header", "Get authentication header with token"),
        ("GetProcessor list", "Get processor list"),
        ("Results will be cached", "Results will be cached"),
        ("Force refresh", "Force refresh"),
        ("Processor list", "Processor list"),
        ("Processor dictionary", "Processor dictionary"),
        ("Platform dictionary", "Platform dictionary"),
        ("For example:", "For example:"),
        ("File paths", "File paths"),
        ("Uploaded BIOS ID", "Uploaded BIOS ID"),
        ("根據 BIOS typeGet revision ID", "Get revision ID based on BIOS type"),
        ("Version name或File paths或 Request ID", "Version name or file path or Request ID"),
        ("Request management", "Request management"),
        ("SavePath", "Save path"),
        ("使用Example", "Usage example"),
        ("GetProcessor list", "Get processor list"),
        ("使用Configuration檔案中的Platform configuration", "Use platform configuration from config file"),
        ("File pathsExample", "File paths example"),
        ("直接傳入Authentication資訊", "Direct credentials"),
        ("平台Configuration", "Platform configuration"),
        ("Default value", "Default values"),
        ("預設 BIOS type", "Default BIOS type"),
        ("預設 purpose", "Default purpose"),
        ("預設Sign type", "Default sign type"),
        ("預設 sign_hp", "Default sign_hp"),
        ("工具方法", "Utility methods"),
        ("Get任意Config value", "Get arbitrary config value"),
        ("支援點號Path", "Supports dot notation path"),
        ("Config key", "Configuration key"),
        ("Config value", "Configuration value"),
        ("SetConfig value", "Set configuration value"),
        ("SaveConfiguration到檔案", "Save configuration to file"),
        ("PrintCurrent configuration", "Print current configuration"),
        ("Hide password", "Hide password"),
        ("載入Configuration", "Load configuration"),
        ("Get二進制檔案完整Path", "Get full path for binary file"),
        ("Filename", "Filename"),
        ("完整Path", "Full path"),
        ("GetDownload檔案完整Path", "Get full path for download file"),
        ("Get token 檔案完整Path", "Get full path for token file"),
        ("Token Filename", "Token filename"),
    ]
    
    for old, new in fixes:
        content = content.replace(old, new)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed: {filepath}")

if __name__ == "__main__":
    files = ["bvm_config.py", "bvm_client.py", "psp_replacement_v2.py"]
    for f in files:
        fix_file(f)
    print("\nAll files fixed!")
