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
    print(f"Error: Input file '{xlsx_path}' does not exist. Please check the file path.")
    exit()

try:
    df = pd.read_excel(xlsx_path, header=None, engine='openpyxl')
    print(f"Info: Successfully read file: '{xlsx_path}'")

    for start_row, end_row, title in data_blocks_info:
        print(f"Processing: '{title}' (Excel rows {start_row + 1} to {end_row})")

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
            print(f"Warning: Index error while processing block '{title}'.")
            print(f"   Please check if range (rows {start_row}-{end_row-1}, columns {column_indices}) is valid in '{xlsx_path}'.")
            print(f"   Skipping this block.")
        except Exception as e:
            print(f"Warning: Unexpected error while processing block '{title}': {e}. Skipping this block.")

    if final_markdown:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        print(f"Success: Exported Markdown file to: '{output_path}'")
    else:
        print("Error: No Markdown content generated. Please check the input file format and script range definitions.")

except FileNotFoundError:
    print(f"Error: Input file '{xlsx_path}' not found or cannot be read.")
except ImportError as e:
    print(f"Error: Required Python library missing ({e}).")
    print(f"   Please ensure pandas, openpyxl, and tabulate are installed.")
    print(f"   Run: pip install pandas openpyxl tabulate")
except Exception as e:
    print(f"Error: Unexpected error occurred: {e}")

