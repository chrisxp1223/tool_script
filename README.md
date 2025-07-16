# Firmware Development Tools

UEFI/Coreboot 開發工具腳本集合，整合 Taskmaster AI 智能任務管理。

## 🚀 快速開始

### 初始化 Taskmaster AI

```bash
# 安裝依賴
npm install

# 初始化 Taskmaster AI
node init_taskmaster.js

# 或直接執行
npm run taskmaster
```

### 環境設定

確保設定 `GOOGLE_API_KEY` 環境變數：

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

或在 `.env` 檔案中設定：

```
GOOGLE_API_KEY=your-api-key-here
```

## 📁 專案結構

```
tool_script/
├── package.json              # Node.js 專案配置
├── taskmaster.config.js      # Taskmaster AI 配置
├── init_taskmaster.js        # 初始化腳本
├── logs/                     # 日誌目錄
├── batch/                    # Windows 批次檔案
├── shellclass/              # Shell 腳本類別
├── py/                      # Python 腳本
├── sample/                  # 範例檔案
└── *.sh                     # Shell 腳本
```

## 🔧 可用腳本

### 核心腳本
- `coreboot_build.sh` - Coreboot 建置腳本
- `flash.sh` - 韌體燒錄腳本
- `flash_cb` - Coreboot 燒錄工具
- `flashit` - 通用燒錄工具

### 測試腳本
- `smu_read.sh` - SMU 讀取測試
- `stt_check.sh` - STT 檢查測試
- `suspend_test.sh` - 休眠測試

### 工具腳本
- `apcb_gen.sh` - APCB 生成工具
- `crosenv` - Chrome OS 環境設定
- `RSC` - RSC 工具

## 🤖 Taskmaster AI 功能

### 任務管理
- **智能任務排程** - 自動優化任務執行順序
- **並發控制** - 防止資源衝突
- **錯誤重試** - 自動處理失敗任務
- **進度追蹤** - 即時監控任務狀態

### 配置選項
- **預設任務** - 3個並發，5分鐘超時
- **韌體任務** - 1個並發，10分鐘超時
- **建置任務** - 2個並發，15分鐘超時

### 日誌與通知
- JSON 格式日誌
- 控制台和檔案通知
- 詳細錯誤追蹤

## 📋 使用範例

### 基本使用
```bash
# 啟動 Taskmaster AI
npm run taskmaster

# 直接執行
npx task-master-ai

# 查看版本
npx task-master-ai --version
```

### 自定義配置
編輯 `taskmaster.config.js` 來調整：
- API 金鑰設定
- 任務超時時間
- 並發數量
- 日誌等級

## 🔍 故障排除

### 常見問題
1. **API 金鑰錯誤** - 檢查 `GOOGLE_API_KEY` 環境變數
2. **權限問題** - 確保腳本有執行權限
3. **網路連接** - 檢查網路連接狀態

### 日誌檢查
```bash
# 查看日誌
tail -f logs/taskmaster.log

# 檢查錯誤
grep "ERROR" logs/taskmaster.log
```

## 📝 授權

MIT License - 詳見 LICENSE 檔案

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！
