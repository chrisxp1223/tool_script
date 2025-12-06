# BVM 配置系統快速入門

## 環境設置 (一次性)

### 方式 1: 使用虛擬環境 (推薦)

```bash
# 1. 建立虛擬環境
python3 -m venv venv

# 2. 啟動虛擬環境
source venv/bin/activate    # Linux/WSL/Mac
# 或
venv\Scripts\activate       # Windows

# 3. 安裝依賴
pip install -r requirements.txt
```

### 方式 2: 使用快速啟動腳本

```bash
# 啟動並顯示環境資訊
source activate.sh
```

### 方式 3: 系統級安裝 (不推薦)

```bash
pip install --break-system-packages -r requirements.txt
```

## 配置設定

### 1. 編輯配置檔案

編輯 `bvm_config.yaml`:

```yaml
bvm:
  username: 你的使用者名稱    # 修改這裡
  password: 你的密碼          # 修改這裡

paths:
  # Windows 路徑使用 \ 或 / 都可以
  binary_dir: D:\BVM\binaries
  download_dir: D:\BVM\downloads
  token_dir: D:\BVM\tokens

platform:
  processor_name: Rembrandt - Family 19h
  platform_name: Rev_RMB_Mayan_Insyde_EDKII
  psp_config: RMB
```

### 2. 測試配置

```bash
# 測試配置載入
python bvm_config.py

# 執行所有範例
python example_usage.py
```

## 使用範例

### 範例 1: 基本使用

```python
from bvm_config import BvmConfig
from bvm_client import BvmClient

# 載入配置
config = BvmConfig("bvm_config.yaml")

# 建立客戶端 (會自動登入)
client = BvmClient(config=config)

# 取得處理器清單
processors = client.get_processor_list()
print(f"找到 {len(processors)} 個處理器")
```

### 範例 2: PSP Replacement

```python
from bvm_config import BvmConfig
from bvm_client import BvmClient

# 載入配置
config = BvmConfig("bvm_config.yaml")
client = BvmClient(config=config)

# 使用配置的路徑
smu_path = config.get_binary_path("SMU_46.59.0.bin")
download_path = config.get_download_path("output.FD")

# 建立 replacement list
replacementList = [
    {
        "entryType": "IMAGE_ENTRY",
        "type": "0x8",
        "romId": "0x0",
        "instance": "0x0",
        "subProgram": "0x0",
        "operation": 2,  # Modify
        "filename": smu_path,
        "level": "0x2A",
        "dirIndex": "0x1",
        "detail": "SMU update",
        "isPspEntry": True
    }
]

# 使用配置的平台設定
processor_name = config.processor_name
platform_name = config.platform_name
psp_config = config.psp_config

print(f"Platform: {processor_name} / {platform_name}")
print(f"PSP Config: {psp_config}")
print(f"SMU Binary: {smu_path}")
print(f"Output: {download_path}")
```

### 範例 3: 檔案路徑處理

```python
from bvm_config import BvmConfig

config = BvmConfig("bvm_config.yaml")

# 自動處理路徑
smu_file = config.get_binary_path("SMU.bin")
# → D:\BVM\binaries\SMU.bin

token_file = config.get_token_path("token.stkn")
# → D:\BVM\tokens\token.stkn

download_file = config.get_download_path("output.FD")
# → D:\BVM\downloads\output.FD

# 目錄會自動建立
print(f"Binary dir exists: {config.binary_dir.exists()}")
```

## 常見問題

### Q: 虛擬環境每次都要啟動嗎？

**A:** 是的。每次新開終端機都需要啟動：

```bash
source venv/bin/activate    # Linux/WSL/Mac
venv\Scripts\activate       # Windows
```

或使用快速腳本：
```bash
source activate.sh
```

### Q: 如何知道虛擬環境已啟動？

**A:** 命令提示符前面會有 `(venv)`:

```
(venv) user@machine:~/BVM$
```

### Q: 路徑在 Windows 下怎麼寫？

**A:** 三種方式都可以：

```yaml
# 方式 1: 使用正斜線
binary_dir: D:/BVM/binaries

# 方式 2: 使用雙反斜線
binary_dir: D:\\BVM\\binaries

# 方式 3: 使用單反斜線 + 引號
binary_dir: "D:\BVM\binaries"
```

### Q: 配置檔案放哪裡？

**A:** 預設尋找順序：
1. 當前目錄: `./bvm_config.yaml`
2. 當前目錄: `./bvm_config.yml`
3. 當前目錄: `./bvm_config.json`
4. 使用者目錄: `~/.bvm/config.yaml`

或直接指定：
```python
config = BvmConfig("/path/to/your/config.yaml")
```

### Q: 密碼會不會被提交到 Git？

**A:** 建議在 `.gitignore` 添加：

```
bvm_config.yaml
bvm_config.yml
*_config.yaml
venv/
```

### Q: 可以有多個配置檔案嗎？

**A:** 可以！針對不同平台：

```bash
# 建立不同平台的配置
cp bvm_config.yaml config_rembrandt.yaml
cp bvm_config.yaml config_phoenix.yaml

# 使用不同配置
python your_script.py --config config_phoenix.yaml
```

或在程式中：
```python
rmb_config = BvmConfig("config_rembrandt.yaml")
phx_config = BvmConfig("config_phoenix.yaml")
```

## 下一步

### 整合到現有腳本

將現有的 `PspReplacement.py` 改用配置系統：

```python
# 舊方式
username = "lahan"
password = "*"
downloadPath = "D:\\temp\\1.FD"

# 新方式
from bvm_config import BvmConfig
from bvm_client import BvmClient

config = BvmConfig("bvm_config.yaml")
client = BvmClient(config=config)

downloadPath = config.get_download_path("output.FD")
```

### 建立統一的 CLI 工具

目標：
```bash
# 使用配置執行 PSP replacement
python bvm_tool.py psp --config bvm_config.yaml

# 使用配置執行 CBS override
python bvm_tool.py cbs --config bvm_config.yaml

# 比較 PSP entries
python bvm_tool.py compare --config bvm_config.yaml
```

## 檔案清單

```
BVM/
├── venv/                    # 虛擬環境 (自動建立)
├── bvm_config.py           # 配置管理器
├── bvm_client.py           # BVM 客戶端基礎類別
├── bvm_config.yaml         # 配置檔案 (需編輯)
├── example_usage.py        # 使用範例
├── requirements.txt        # Python 依賴
├── activate.sh             # 快速啟動腳本
├── QUICKSTART.md          # 本文件
├── CONFIG_GUIDE.md        # 詳細配置指南
├── README.md              # BVM 工具說明
└── CLAUDE.md              # Claude Code 指引
```

## 相關文件

- **CONFIG_GUIDE.md**: 完整配置說明和進階用法
- **README.md**: BVM API 工具完整文件
- **example_usage.py**: 7 個實際使用範例

## 需要協助？

執行範例程式查看更多用法：
```bash
python example_usage.py
```

查看詳細文件：
```bash
cat CONFIG_GUIDE.md
```
