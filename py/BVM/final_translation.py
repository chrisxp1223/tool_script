#!/usr/bin/env python3
"""Final cleanup of translations"""

def clean_bvm_client():
    with open("bvm_client.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements = [
        ('"""BVM API BVM API Client Base Class"""', '"""BVM API Client Base Class"""'),
        ('# Method 3: 使用 BvmConfig instance', '# Method 3: Using BvmConfig instance'),
        ('# 嘗試自動Load configuration', '# Try to auto-load configuration'),
        ('# Load configuration', '# Load configuration'),
        ('# Set authentication info', '# Set authentication info'),  
        ('# Auto login', '# Auto login'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open("bvm_client.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Cleaned bvm_client.py")

def clean_bvm_config():
    with open("bvm_config.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # No additional fixes needed
    print("✓ bvm_config.py is clean")

def clean_psp():
    with open("psp_replacement_v2.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements = [
        ('"""PSP entry operation type"""', '"""PSP entry operation type"""'),
        ('# Call parent class initialization (Will auto login)', '# Call parent class initialization (will auto login)'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open("psp_replacement_v2.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Cleaned psp_replacement_v2.py")

if __name__ == "__main__":
    clean_bvm_client()
    clean_bvm_config()
    clean_psp()
    print("\nAll translations cleaned!")
