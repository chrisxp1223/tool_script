import pandas as pd
from tabulate import tabulate
import os

xlsx_path = "dqmap_rmb.xlsx"
output_path = "dqmap_rmb.md"

data_blocks_info = [
    (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
    (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
    (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
    (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
]

column_indices = [0, 1, 3, 5, 7]

output_columns = ["DRAM DQ Lane", "Channel A", "Channel B", "Channel C", "Channel D"]

final_markdown = ""

if not os.path.exists(xlsx_path):
    print(f"❌ 錯誤：輸入檔案 '{xlsx_path}' 不存在。請確認檔案路徑是否正確。")
    exit()

try:
    df = pd.read_excel(xlsx_path, header=None, engine='openpyxl')

    print(f"ℹ️  成功讀取檔案: '{xlsx_path}'")

    for start_row, end_row, title in data_blocks_info:
        print(f"⚙️  正在處理區塊: '{title}' (Excel 列 {start_row + 1} 到 {end_row})")

        try:
            block_slice = df.iloc[start_row:end_row, column_indices]

            block_df = pd.DataFrame(block_slice.values, columns=output_columns).copy()

            for col in ["Channel A", "Channel B", "Channel C", "Channel D"]:
                block_df[col] = pd.to_numeric(block_df[col], errors='coerce').astype('Int64')

            markdown_table = tabulate(
                block_df,
                headers="keys",
                tablefmt="github",
                showindex=False,
                missingval="NaN"
            )

            final_markdown += f"### {title}\n\n"
            final_markdown += markdown_table
            final_markdown += "\n\n"

        except IndexError:
            print(f"⚠️ 警告：處理區塊 '{title}' 時發生索引錯誤。")
            print(f"   請檢查定義的範圍 (列 {start_row}-{end_row-1}, 欄 {column_indices}) 是否在檔案 '{xlsx_path}' 的有效範圍內。")
            print(f"   將跳過此區塊。")
        except Exception as e:
            print(f"⚠️ 警告：處理區塊 '{title}' 時發生未預期的錯誤: {e}。將跳過此區塊。")


    if final_markdown:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        print(f"✅ 成功輸出 Markdown 檔案到：'{output_path}'")
    else:
        print("❌ 錯誤：沒有產生任何 Markdown 內容。請檢查輸入檔案的格式和腳本中的範圍定義。")

except FileNotFoundError:
     print(f"❌ 錯誤：輸入檔案 '{xlsx_path}' 未找到或無法讀取。")
except ImportError as e:
     print(f"❌ 錯誤：缺少必要的 Python 函式庫 ({e})。")
     print(f"   請確認已安裝 pandas, openpyxl, 和 tabulate。")
     print(f"   可以執行: pip install pandas openpyxl tabulate")
except Exception as e:
    print(f"❌ 處理過程中發生未預期的錯誤：{e}")

