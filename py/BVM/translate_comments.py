#!/usr/bin/env python3
"""
Translate Chinese comments to English in Python files
"""

translations = {
    # bvm_config.py
    "建立預設配置檔案": "Create default configuration file",
    "載入配置檔案": "Load configuration file",
    "認證": "Authentication",
    "BVM 使用者名稱": "BVM username",
    "BVM 密碼": "BVM password",
    "BVM 伺服器 URL": "BVM server URL",
    "檔案路徑": "File paths",
    "二進制檔案目錄": "Binary files directory",
    "下載目錄": "Download directory",
    "Token 檔案目錄": "Token files directory",
    "用於 BIOS 簽署": "For BIOS signing",
    "平台設定": "Platform configuration",
    "處理器名稱": "Processor name",
    "平台名稱": "Platform name",
    "預設參數": "Default parameters",
    "預設值": "Default value",
    "取得": "Get",
    "設定": "Set",
    "儲存": "Save",
    "印出": "Print",
    "隱藏密碼": "Hide password",
    "目前配置": "Current configuration",
    "路徑": "Path",
    "範例": "Example",
    "使用範例": "Usage example",
    "基礎": "Basic",
    "完整路徑": "Full path",
    "檔案名稱": "Filename",
    "儲存路徑": "Save path",
    "配置鍵": "Config key",
    "配置值": "Config value",
    "如果未指定，使用原始配置檔案": "If not specified, use original config file",
    "任意配置值": "Arbitrary config value",
    "支援點號路徑": "Supports dot notation path",
    
    # bvm_client.py
    "共享基礎類別": "Shared base class",
    "提供所有 BVM 工具的共通功能": "Provides common functionality for all BVM tools",
    "認證與 token 管理": "Authentication and token management",
    "處理器/平台查詢": "Processor/platform queries",
    "下載功能": "Download functionality",
    "常數": "Constants",
    "配置": "Configuration",
    "登入 BVM 並取得 token": "Login to BVM and get token",
    "取得帶 token 的認證 header": "Get authentication header with token",
    "取得處理器清單": "Get processor list",
    "會快取結果": "Results will be cached",
    "強制重新查詢": "Force refresh",
    "處理器清單": "Processor list",
    "根據名稱查找處理器 ID": "Find processor ID by name",
    "根據名稱查找平台 ID": "Find platform ID by name",
    "處理器字典": "Processor dictionary",
    "平台字典": "Platform dictionary",
    "查找 Weekly BIOS ID": "Find Weekly BIOS ID",
    "版本名稱": "Version name",
    "查找 PI BIOS ID": "Find PI BIOS ID",
    "上傳 User-Generated BIOS": "Upload User-Generated BIOS",
    "BIOS 檔案路徑": "BIOS file path",
    "上傳後的 BIOS ID": "Uploaded BIOS ID",
    "根據 BIOS 類型取得 revision ID": "Get revision ID based on BIOS type",
    "BIOS 類型": "BIOS type",
    "版本名稱或檔案路徑或 Request ID": "Version name or file path or Request ID",
    "請求管理": "Request management",
    "更新請求名稱": "Update request name",
    "請求 ID": "Request ID",
    "新名稱": "New name",
    "下載修改後的 BIOS": "Download modified BIOS",
    "下載完整 tar 檔案": "Download complete tar file",
    
    # psp_replacement_v2.py
    "使用配置系統": "Using configuration system",
    "改進": "Improvements",
    "使用 BvmClient 基礎類別": "Uses BvmClient base class",
    "支援配置檔案": "Supports configuration file",
    "物件導向設計": "Object-oriented design",
    "更好的錯誤處理": "Better error handling",
    "PSP 條目操作類型": "PSP entry operation type",
    "PSP 條目替換客戶端": "PSP entry replacement client",
    "初始化 PSP Replacer": "Initialize PSP Replacer",
    "可選": "Optional",
    "如果使用 config": "If using config",
    "呼叫父類別初始化": "Call parent class initialization",
    "會自動登入": "Will auto login",
    "取得可用的操作類型": "Get available operation types",
    "操作類型字典": "Operation type dictionary",
    "取得操作類型字串": "Get operation type string",
    "操作類型": "Operation type",
    "例如": "For example",
    "操作類型字串": "Operation type string",
    "生成 PSP 請求": "Generate PSP request",
    "目的": "Purpose",
    "PSP 配置": "PSP configuration",
    "上傳 PSP 條目": "Upload PSP entries",
    "替換清單": "Replacement list",
    "跳過 Remove 操作和 type 0x7": "Skip Remove operation and type 0x7",
    "建立上傳 URL": "Build upload URL",
    "需要 offset": "Requires offset",
    "上傳檔案": "Upload file",
    "提交 PSP 請求": "Submit PSP request",
    "簽署類型": "Sign type",
    "簽署 HP": "Sign HP",
    "簽署使用者名稱": "Sign username",
    "簽署密碼": "Sign password",
    "簽署 SP 函數": "Sign SP function",
    "使用預設認證資訊": "Use default credentials",
    "更新檔名為 BVM 格式": "Update filename to BVM format",
    "特殊處理": "Special handling",
    "完整的 PSP 條目替換流程": "Complete PSP entry replacement workflow",
    "從配置讀取": "Read from config",
    "必填": "Required",
    "從配置讀取預設值": "Read default values from config",
    "檢查必填參數": "Check required parameters",
    "生成請求": "Generate request",
    "上傳條目": "Upload entries",
    "提交請求": "Submit request",
    "下載": "Download",
    "如果指定路徑": "If path is specified",
    "載入配置": "Load configuration",
    "修改 SMU 韌體": "Replace SMU firmware",
    "使用配置的路徑": "Use configured paths",
    "執行替換": "Execute replacement",
    "註解掉實際執行，避免意外修改": "Commented out to avoid accidental execution",
    "指定版本": "Specify version",
    "實際執行已註解，取消註解即可執行": "Actual execution is commented, uncomment to run",
}

import sys
import re

def translate_file(filepath):
    """Translate Chinese comments in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for zh, en in translations.items():
        # Match in comments and docstrings
        content = content.replace(zh, en)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Translated: {filepath}")
        return True
    else:
        print(f"- No changes: {filepath}")
        return False

if __name__ == "__main__":
    files = [
        "bvm_config.py",
        "bvm_client.py",
        "psp_replacement_v2.py"
    ]
    
    translated = 0
    for file in files:
        if translate_file(file):
            translated += 1
    
    print(f"\nTranslated {translated}/{len(files)} files")
