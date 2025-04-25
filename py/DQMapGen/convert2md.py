import pandas as pd
from tabulate import tabulate
import numpy as np

# 1️⃣ 讀取 Excel 檔案
xlsx_path = "test_dqmap.xlsx"  # ← 請根據實際路徑調整
df = pd.read_excel(xlsx_path, sheet_name=0)

# 2️⃣ 去除多餘欄位（如 Unnamed）
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# 3️⃣ 自動尋找每段開始位置（透過包含 [7:0] 或 [15:8] 的標籤）
group_starts = df[df.iloc[:, 0].astype(str).str.contains(r"\[7:0\]|\[15:8\]", na=False)].index.tolist()

# 4️⃣ 分段擷取資料，並統一格式（每段強制為 5 欄）
groups = []
expected_columns = ["DRAM DQ Lane", "Channel A", "Channel B", "Channel C", "Channel D"]

for i in range(4):
    start = group_starts[i]
    end = group_starts[i + 1] if i + 1 < len(group_starts) else len(df)
    group = df.iloc[start + 1:end].reset_index(drop=True)

    # 補齊欄數至 5 欄
    while group.shape[1] < 5:
        group[f"FILL_{group.shape[1]}"] = np.nan
    group.columns = expected_columns + list(group.columns[5:])
    group = group[expected_columns]

    groups.append(group)

# 5️⃣ 區段標題
titles = [
    "[7:0] Lower Byte Group",
    "[15:8] Upper Byte Group",
    "[7:0] Lower Byte Group (B Side)",
    "[15:8] Upper Byte Group (B Side)"
]

# 6️⃣ 產生 Markdown 格式的表格
def generate_markdown(title, dataframe):
    markdown = f"### {title}\n\n"
    markdown += tabulate(dataframe, headers="keys", tablefmt="github", showindex=False)
    markdown += "\n\n"
    return markdown

# 7️⃣ 組合所有 markdown 區塊
final_markdown = ""
for title, group_df in zip(titles, groups):
    final_markdown += generate_markdown(title, group_df)

# 8️⃣ 輸出為 .md 檔案
output_path = "generated_dqmap.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_markdown)

print(f"✅ 已輸出為：{output_path}")
