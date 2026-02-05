import pandas as pd
from tabulate import tabulate
import os
import argparse

# Platform Excel configurations
# All platforms use the same format initially, can be customized later
PLATFORM_EXCEL_CONFIGS = {
    'rmb': {
        'name': 'Rembrandt',
        'family': 'rembrandt',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    },
    'phx': {
        'name': 'Phoenix',
        'family': 'phoenix',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    },
    'hpt': {
        'name': 'Hawkpoint',
        'family': 'phoenix',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    },
    'stx': {
        'name': 'Strix',
        'family': 'strix',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    },
    'krk': {
        'name': 'Krackan',
        'family': 'strix',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    },
    'gpt': {
        'name': 'Granite Point',
        'family': 'strix',
        'data_blocks': [
            (4, 12, "[7:0] Lower Byte Group (MAA/MBA/MCA/MDA)"),
            (13, 21, "[15:8] Upper Byte Group (MAA/MBA/MCA/MDA)"),
            (22, 30, "[7:0] Lower Byte Group (MAB/MBB/MCB/MDB)"),
            (31, 39, "[15:8] Upper Byte Group (MAB/MBB/MCB/MDB)")
        ],
        'column_indices': [0, 1, 3, 5, 7]
    }
}

OUTPUT_COLUMNS = ["DRAM DQ Lane", "Channel A", "Channel B", "Channel C", "Channel D"]


def parse_command_line_args():
    """
    Parse command line arguments to determine which platform to process.

    Returns:
        str: The selected platform identifier
    """
    parser = argparse.ArgumentParser(description='Excel to Markdown Converter for DQ Map')
    platform_group = parser.add_mutually_exclusive_group(required=True)
    # Rembrandt family
    platform_group.add_argument('--rmb', action='store_const', const='rmb', dest='platform',
                              help='Convert Rembrandt Excel file')
    # Phoenix family
    platform_group.add_argument('--phx', action='store_const', const='phx', dest='platform',
                              help='Convert Phoenix Excel file')
    platform_group.add_argument('--hpt', action='store_const', const='hpt', dest='platform',
                              help='Convert Hawkpoint Excel file (Phoenix family)')
    # Strix family
    platform_group.add_argument('--stx', action='store_const', const='stx', dest='platform',
                              help='Convert Strix Excel file')
    platform_group.add_argument('--krk', action='store_const', const='krk', dest='platform',
                              help='Convert Krackan Excel file (Strix family)')
    platform_group.add_argument('--gpt', action='store_const', const='gpt', dest='platform',
                              help='Convert Granite Point Excel file (Strix family)')

    args = parser.parse_args()
    return args.platform


def convert_excel_to_markdown(platform):
    """
    Convert Excel DQ map file to Markdown format.

    Args:
        platform (str): Platform identifier (rmb, phx, hpt, stx, krk, gpt)

    Returns:
        bool: True if conversion successful, False otherwise
    """
    config = PLATFORM_EXCEL_CONFIGS.get(platform)
    if not config:
        print(f"Error: Unknown platform '{platform}'")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    xlsx_path = os.path.join(input_dir, f"dqmap_{platform}.xlsx")
    output_path = os.path.join(input_dir, f"dqmap_{platform}.md")

    if not os.path.exists(xlsx_path):
        print(f"Error: Input file '{xlsx_path}' does not exist. Please check the file path.")
        return False

    final_markdown = ""

    try:
        df = pd.read_excel(xlsx_path, header=None, engine='openpyxl')
        print(f"Info: Successfully read file: '{xlsx_path}'")

        data_blocks_info = config['data_blocks']
        column_indices = config['column_indices']

        for start_row, end_row, title in data_blocks_info:
            print(f"Processing: '{title}' (Excel rows {start_row + 1} to {end_row})")

            try:
                block_slice = df.iloc[start_row:end_row, column_indices]
                block_df = pd.DataFrame(block_slice.values, columns=OUTPUT_COLUMNS).copy()

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
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)
            print(f"Success: Exported Markdown file to: '{output_path}'")
            return True
        else:
            print("Error: No Markdown content generated. Please check the input file format and script range definitions.")
            return False

    except FileNotFoundError:
        print(f"Error: Input file '{xlsx_path}' not found or cannot be read.")
        return False
    except ImportError as e:
        print(f"Error: Required Python library missing ({e}).")
        print(f"   Please ensure pandas, openpyxl, and tabulate are installed.")
        print(f"   Run: pip install pandas openpyxl tabulate")
        return False
    except Exception as e:
        print(f"Error: Unexpected error occurred: {e}")
        return False


if __name__ == "__main__":
    platform = parse_command_line_args()
    print(f"Converting DQ map for platform: {PLATFORM_EXCEL_CONFIGS[platform]['name']}")
    convert_excel_to_markdown(platform)
