import pandas as pd
from tabulate import tabulate
import os # 匯入 os 模組以檢查檔案是否存在

# --- 設定區 ---
xlsx_path = "dqmap_rmb.xlsx" # 輸入的 Excel 檔案路徑
output_path = "dqmap_rmb.md" # 輸出的 Markdown 檔案路徑 (使用新名稱)

# 根據圖片和 CSV 分析，定義四個資料區塊的資訊
# 每個 tuple 包含: (起始列, 結束列(不含), 區塊標題)
# 列索引是 0-based (假設使用 pandas 讀取且 header=None)
# 這些索引對應到實際資料列 (例如 DQ7, 23, 15, ...)
data_blocks_info = [
    # 區塊 1: [7:0] Lower Byte Group (A Side)
    (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"), # Excel 中的第 5 到 12 列
    # 區塊 2: [15:8] Upper Byte Group (A Side)
    (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"), # Excel 中的第 14 到 21 列
    # 區塊 3: [7:0] Lower Byte Group (B Side)
    (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"), # Excel 中的第 23 到 30 列
    # 區塊 4: [15:8] Upper Byte Group (B Side)
    (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")  # Excel 中的第 32 到 39 列
]

# 定義要提取的欄位 0-based 索引
# 對應到: DQ 標籤, Channel A, Channel B, Channel C, Channel D 的 Pin 腳編號
column_indices = [0, 1, 3, 5, 7]

# 定義最終輸出的標準欄位名稱
output_columns = ["DRAM DQ Lane", "Channel A", "Channel B", "Channel C", "Channel D"]

# --- 腳本主要邏輯 ---
final_markdown = "" # 用於儲存最終 Markdown 內容的字串

# 檢查輸入檔案是否存在
if not os.path.exists(xlsx_path):
    print(f"❌ 錯誤：輸入檔案 '{xlsx_path}' 不存在。請確認檔案路徑是否正確。")
    exit() # 如果檔案不存在，則結束程式

try:
    # 讀取 Excel 檔案，不假設任何表頭列 (header=None)
    # 這樣可以確保我們使用 .iloc 進行精確的位置切片
    df = pd.read_excel(xlsx_path, header=None, engine='openpyxl')

    print(f"ℹ️  成功讀取檔案: '{xlsx_path}'")

    # 逐一處理定義好的每個資料區塊
    for start_row, end_row, title in data_blocks_info:
        print(f"⚙️  正在處理區塊: '{title}' (Excel 列 {start_row + 1} 到 {end_row})")

        # 使用 .iloc 根據定義好的行列索引，提取當前區塊的資料
        try:
            # 先選取列範圍，再選取欄範圍
            block_slice = df.iloc[start_row:end_row, column_indices]

            # 建立一個新的 DataFrame，包含提取的資料和標準化的欄位名稱
            # 使用 .copy() 避免潛在的 SettingWithCopyWarning
            block_df = pd.DataFrame(block_slice.values, columns=output_columns).copy()

            # (可選) 將 Pin 腳編號轉換為整數型別，以便在 Markdown 中保持一致格式
            # 使用 Int64 型別可以支援 NaN (缺失值)
            for col in ["Channel A", "Channel B", "Channel C", "Channel D"]:
                # errors='coerce' 會將無法轉換的值設為 NaN
                block_df[col] = pd.to_numeric(block_df[col], errors='coerce').astype('Int64')

            # 為當前區塊產生 Markdown 表格
            markdown_table = tabulate(
                block_df,
                headers="keys",          # 使用 DataFrame 的欄位名稱作為表頭
                tablefmt="github",       # 指定 Markdown 表格的樣式 (GitHub 風格)
                showindex=False,         # 不顯示 DataFrame 的索引
                missingval="NaN"         # 將 Pandas 中的 NaN/NA 值顯示為 "NaN" 字串
            )

            # 將區塊標題和產生的 Markdown 表格附加到最終結果字串
            final_markdown += f"### {title}\n\n" # 加入三級標題
            final_markdown += markdown_table      # 加入表格
            final_markdown += "\n\n"              # 加入換行，分隔不同區塊

        except IndexError:
            # 如果 .iloc 切片超出 DataFrame 的實際邊界，會引發此錯誤
            print(f"⚠️ 警告：處理區塊 '{title}' 時發生索引錯誤。")
            print(f"   請檢查定義的範圍 (列 {start_row}-{end_row-1}, 欄 {column_indices}) 是否在檔案 '{xlsx_path}' 的有效範圍內。")
            print(f"   將跳過此區塊。")
        except Exception as e:
            # 捕捉其他可能的錯誤
            print(f"⚠️ 警告：處理區塊 '{title}' 時發生未預期的錯誤: {e}。將跳過此區塊。")


    # 將組合好的 Markdown 內容寫入指定的輸出檔案
    if final_markdown: # 確保有內容可以寫入
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        print(f"✅ 成功輸出 Markdown 檔案到：'{output_path}'")
    else:
        # 如果 final_markdown 是空的，表示沒有成功處理任何區塊
        print("❌ 錯誤：沒有產生任何 Markdown 內容。請檢查輸入檔案的格式和腳本中的範圍定義。")

except FileNotFoundError:
     # read_excel 可能引發的錯誤
     print(f"❌ 錯誤：輸入檔案 '{xlsx_path}' 未找到或無法讀取。")
except ImportError as e:
     # 如果缺少必要的函式庫
     print(f"❌ 錯誤：缺少必要的 Python 函式庫 ({e})。")
     print(f"   請確認已安裝 pandas, openpyxl, 和 tabulate。")
     print(f"   可以執行: pip install pandas openpyxl tabulate")
except Exception as e:
    # 捕捉其他未預期的錯誤
    print(f"❌ 處理過程中發生未預期的錯誤：{e}")

