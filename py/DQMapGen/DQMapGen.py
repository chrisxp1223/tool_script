# Copyright 2024 CPWang and GPT]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import logging
import os
import sys
import itertools
import argparse

from convert2md import convert_excel_to_markdown, PLATFORM_EXCEL_CONFIGS

# Set up logging configuration
def setup_logging():
    """Configure logging with custom format and level.

    Sets up logging configuration with a specific format that includes timestamp,
    log level, and message. The logger is configured to write to a log file only,
    without outputting to the console.

    The log file is named 'dqmap_generator.log' and will be created in the
    current working directory.

    Usage:
        logger = setup_logging()
        logger.info("Application started")
        logger.error("An error occurred: %s", error_message)
        logger.debug("Debug information")

    Returns:
        logging.Logger: Configured logger instance for the current module.
    """
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Add only file handler (no console output)
    file_handler = logging.FileHandler('dqmap_generator.log')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    return logger

# Create logger instance
logger = setup_logging()

# Dictionary for mapping platform identifiers to their configurations
PLATFORM_CONFIGS = {
    'rmb': {
        'name': 'Rembrandt',
        'family': 'rembrandt',
        'input_file': 'rmb',
        'header_format': 'RMB_FORMAT',
        'data_pattern': 'MEM_MX_DATA'
    },
    'phx': {
        'name': 'Phoenix',
        'family': 'phoenix',
        'input_file': 'phx',
        'header_format': 'PHX_FORMAT',
        'data_pattern': 'MEM_PHX_DATA'
    },
    'hpt': {
        'name': 'Hawkpoint',
        'family': 'phoenix',
        'input_file': 'hpt',
        'header_format': 'HPT_FORMAT',
        'data_pattern': 'MEM_HPT_DATA'
    },
    'stx': {
        'name': 'Strix',
        'family': 'strix',
        'input_file': 'stx',
        'header_format': 'STX_FORMAT',
        'data_pattern': 'MEM_STX_DATA'
    },
    'krk': {
        'name': 'Krackan',
        'family': 'strix',
        'input_file': 'stx',
        'header_format': 'KRK_FORMAT',
        'data_pattern': 'MEM_KRK_DATA'
    },
    'gpt': {
        'name': 'Granite Point',
        'family': 'strix',
        'input_file': 'stx',
        'header_format': 'GPT_FORMAT',
        'data_pattern': 'MEM_GPT_DATA'
    }
}

def read_dqmap_file(file_path):
    """
    Check if a given file exists and read its contents.

    Args:
        file_path (str): The path to the dqmap file to read.

    Returns:
        tuple: (bool, str) - (success status, file contents or error message)
    """
    try:
        if not os.path.exists(file_path):
            return False, f"Error: File not found at {file_path}"

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if not content:
            return False, f"Error: File is empty at {file_path}"

        print(f"\n--- Content of {os.path.basename(file_path)} ---")
        print(content)
        print(f"--- End of {os.path.basename(file_path)} Content ---\n")
        # ---------------------------------------------

        return True, content

    except Exception as e:
        return False, f"Error reading file {file_path}: {str(e)}"

def parse_dqmap_content(content):
    """
    Parses the content of the dqmap.md file to extract data groups.

    Args:
        content (str): The content read from the dqmap.md file.

    Returns:
        list or None: A list containing 16 lists (data groups),
                      or None if parsing fails.
    """
    print("Parsing dqmap.md content...")

    try:
        # Initialize the mapping structure for each channel and side
        mapping = {
            'MAA': {'lower': [None]*8, 'upper': [None]*8},
            'MAB': {'lower': [None]*8, 'upper': [None]*8},
            'MBA': {'lower': [None]*8, 'upper': [None]*8},
            'MBB': {'lower': [None]*8, 'upper': [None]*8},
            'MCA': {'lower': [None]*8, 'upper': [None]*8},
            'MCB': {'lower': [None]*8, 'upper': [None]*8},
            'MDA': {'lower': [None]*8, 'upper': [None]*8},
            'MDB': {'lower': [None]*8, 'upper': [None]*8}
        }

        # Flag to track the current section we're parsing
        current_section = None
        is_b_side = False

        # Split the content into lines for processing
        lines = content.strip().split('\n')

        # Process each line
        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Identify which section we're in based on the markdown headers
            if line.startswith('###'):
                if '[7:0]' in line:
                    current_section = 'lower'
                elif '[15:8]' in line:
                    current_section = 'upper'

                # Check if this is B side by looking at the channel names in parentheses
                if 'MAB/MBB/MCB/MDB' in line:
                    is_b_side = True
                elif 'MAA/MBA/MCA/MDA' in line:
                    is_b_side = False
                side_name = 'B' if is_b_side else 'A'
                print(f"Section: {current_section}, Side: {side_name}")
                continue

            # Skip header rows and empty lines
            if line.startswith('|') and "DRAM DQ Lane" not in line and "---" not in line:
                # Parse the table row
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 5:  # Ensure valid row format (at least 5 parts after splitting and cleaning)
                    try:
                        # Extract DQ lane number
                        dq_lane = int(parts[0].replace("DQ", ""))

                        # Extract pin numbers for each channel
                        channel_a_pin = int(parts[1])
                        channel_b_pin = int(parts[2])
                        channel_c_pin = int(parts[3])
                        channel_d_pin = int(parts[4])

                        # Calculate correct index for upper section
                        idx = dq_lane if current_section == 'lower' else dq_lane - 8

                        # Store in the appropriate section and side
                        if not is_b_side:  # A side
                            mapping['MAA'][current_section][idx] = channel_a_pin
                            mapping['MBA'][current_section][idx] = channel_b_pin
                            mapping['MCA'][current_section][idx] = channel_c_pin
                            mapping['MDA'][current_section][idx] = channel_d_pin
                        else:  # B side
                            mapping['MAB'][current_section][idx] = channel_a_pin
                            mapping['MBB'][current_section][idx] = channel_b_pin
                            mapping['MCB'][current_section][idx] = channel_c_pin
                            mapping['MDB'][current_section][idx] = channel_d_pin
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Could not parse line: {line}")
                        print(f"Error details: {str(e)}")
                        continue

        # Extract data groups in the specified order
        data_groups = [
            mapping['MAA']['lower'],  # Group 1: MAA lower (DQ0-DQ7)
            mapping['MAA']['upper'],  # Group 2: MAA upper (DQ8-DQ15)
            mapping['MAB']['lower'],  # Group 3: MAB lower (DQ0-DQ7)
            mapping['MAB']['upper'],  # Group 4: MAB upper (DQ8-DQ15)
            mapping['MBA']['lower'],  # Group 5: MBA lower (DQ0-DQ7)
            mapping['MBA']['upper'],  # Group 6: MBA upper (DQ8-DQ15)
            mapping['MBB']['lower'],  # Group 7: MBB lower (DQ0-DQ7)
            mapping['MBB']['upper'],  # Group 8: MBB upper (DQ8-DQ15)
            mapping['MCA']['lower'],  # Group 9: MCA lower (DQ0-DQ7)
            mapping['MCA']['upper'],  # Group 10: MCA upper (DQ8-DQ15)
            mapping['MCB']['lower'],  # Group 11: MCB lower (DQ0-DQ7)
            mapping['MCB']['upper'],  # Group 12: MCB upper (DQ8-DQ15)
            mapping['MDA']['lower'],  # Group 13: MDA lower (DQ0-DQ7)
            mapping['MDA']['upper'],  # Group 14: MDA upper (DQ8-DQ15)
            mapping['MDB']['lower'],  # Group 15: MDB lower (DQ0-DQ7)
            mapping['MDB']['upper']   # Group 16: MDB upper (DQ8-DQ15)
        ]

        # Print all groups for user validation
        print("\n--- Parsed DQ Groups ---")
        for i, (channel, section) in enumerate(zip(
            ['MAA', 'MAA', 'MAB', 'MAB', 'MBA', 'MBA', 'MBB', 'MBB',
             'MCA', 'MCA', 'MCB', 'MCB', 'MDA', 'MDA', 'MDB', 'MDB'],
            ['lower', 'upper', 'lower', 'upper', 'lower', 'upper', 'lower', 'upper',
             'lower', 'upper', 'lower', 'upper', 'lower', 'upper', 'lower', 'upper']
        )):
            group_num = i + 1
            print(f"Group {group_num}: {channel}-{section} (DQ{'0-7' if section=='lower' else '8-15'}): {data_groups[i]}")
        print("--- End of Parsed DQ Groups ---\n")

        # Validate the data
        for i, group in enumerate(data_groups):
            if None in group:
                print(f"Warning: Group {i+1} contains None values: {group}")
                # Replace None with 0 for simplicity
                data_groups[i] = [0 if x is None else x for x in group]

        return data_groups

    except Exception as e:
        print(f"Error parsing dqmap.md content: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_mem_data_groups(offsets, data_groups):
    """
    Generate memory data groups based on offsets and data groups.

    Args:
        offsets: List of offsets for each channel [MA0,MA8,MA16,MA24, MB0,MB8,MB16,MB24, ...]
        data_groups: List of DQ pin mappings for each channel

    Returns:
        List of processed groups with MEM_MX_DATA_XX format
    """
    result = []

    # Process each channel (MA, MB, MC, MD)
    for channel_idx in range(4):
        channel_offsets = offsets[channel_idx * 4:(channel_idx + 1) * 4]

        # Process A-side lower byte group
        a_lower_group = []
        a_data = data_groups[channel_idx * 4]
        for dq_idx, pin in enumerate(a_data):
            offset = channel_offsets[0]
            value = pin
            if value >= 8:
                value -= 8
            value += offset
            a_lower_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(a_lower_group)

        # Process A-side upper byte group
        a_upper_group = []
        a_data = data_groups[channel_idx * 4 + 1]
        for dq_idx, pin in enumerate(a_data):
            offset = channel_offsets[1]
            value = pin
            if value >= 8:
                value -= 8
            value += offset
            a_upper_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(a_upper_group)

        # Process B-side lower byte group
        b_lower_group = []
        for dq_idx in range(8):
            offset = channel_offsets[2]
            value = dq_idx + offset
            b_lower_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(b_lower_group)

        # Process B-side upper byte group
        b_upper_group = []
        for dq_idx in range(8):
            offset = channel_offsets[3]
            value = dq_idx + offset
            b_upper_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(b_upper_group)

    return result

def get_offsets_interactively():
    """
    Interactively prompts the user to enter 4 offsets (0, 8, 16, 24) for each
    channel (MA, MB, MC, MD). Enter 'd' once to apply default values to all channels.

    Returns:
        list[list[int]]: A list containing 4 lists of offsets
    """
    expected_offsets = {0, 8, 16, 24}
    default_offsets = [0, 8, 16, 24]
    channel_names = ["MA", "MB", "MC", "MD"]
    all_offset_groups = []

    print("Please enter the offset values (0 8 16 24) for each channel,")
    print("or enter 'd' to use default values (0 8 16 24) for ALL channels:")

    # First check if user wants to use default values for all channels
    print("Use defaults for all channels? (d/n): ", end="")
    sys.stdout.flush()
    try:
        use_defaults = input().strip().lower()
        if use_defaults == 'd':
            # Apply default values to all channels
            for channel in channel_names:
                all_offset_groups.append(default_offsets.copy())
                print(f"Using default offsets for {channel}: {default_offsets}")
            return all_offset_groups
    except (EOFError, KeyboardInterrupt):
        logger.error("\nOperation interrupted. Exiting.")
        sys.exit(1)

    # If not using defaults, proceed with individual channel input
    for channel in channel_names:
        current_channel_offsets = None

        while current_channel_offsets is None:
            print(f"{channel}: ", end="")
            sys.stdout.flush()
            try:
                user_input = input().strip().lower()

                if not user_input:
                    print(f"Error: No input provided for {channel}. Please try again.")
                    continue

                input_parts = user_input.split()
                entered_offsets = [int(part) for part in input_parts]

                if len(entered_offsets) != 4:
                    print(f"Error: Exactly 4 offsets required. You entered {len(entered_offsets)}.")
                    continue

                entered_set = set(entered_offsets)
                if entered_set != expected_offsets:
                    print(f"Error: Channel {channel} offsets must be exactly 0, 8, 16, 24.")
                    print(f"      You entered: {entered_offsets}")
                    print(f"      Expected: {sorted(list(expected_offsets))}")
                    continue

                current_channel_offsets = entered_offsets

            except ValueError:
                print(f"Error: Offsets must be valid integers. Please check your input.")
                continue
            except (EOFError, KeyboardInterrupt):
                logger.critical("\nOperation interrupted. Exiting.")
                sys.exit(1)

        all_offset_groups.append(current_channel_offsets)

    return all_offset_groups

def get_file_name(platform_name):
    """
    Retrieves the full path of the markdown file for the given platform
    from the 'input' directory located in the same directory as the script.

    Uses the 'input_file' field from PLATFORM_CONFIGS to determine which
    input file to use. This allows multiple platforms to share the same
    input file (e.g., krk and gpt use stx input file).

    Args:
        platform_name (str): The name of the platform (e.g., 'rmb', 'hpt', 'stx').

    Returns:
        str or None: The full path of the markdown file if found, otherwise None.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_dir = os.path.join(script_dir, 'input')

        if not os.path.exists(input_dir):
            logger.error(f"Input directory not found at {input_dir}")
            return None

        # Use input_file from config, fallback to platform_name if not specified
        input_file_key = PLATFORM_CONFIGS.get(platform_name, {}).get('input_file', platform_name)
        expected_filename = f"dqmap_{input_file_key}.md"
        file_path = os.path.join(input_dir, expected_filename)

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        # TODO: use a better way to determine the file name and not use global variables here
        print(f"Found dqmap file: {file_path}")
        global dqmap_filename
        dqmap_filename = file_path
        return file_path

    except Exception as e:
        logger.error(f"Error retrieving markdown file path: {str(e)}")
        return None

def parse_command_line_args():
        """
        Parse command line arguments to determine which platform configuration to use.

        Returns:
            argparse.Namespace: Parsed arguments with 'platform' and 'from_excel' attributes
        """
        # TODO: Modulize the architecture to easily support older and newer platforms
        # TODO: Implement a plugin system for platform-specific code and configurations
        # TODO: Create a configuration file format for defining new platforms without code changes

        parser = argparse.ArgumentParser(
            description='DQ Map Generator Tool',
            epilog='''Examples:
  python DQMapGen.py --rmb                 Convert from existing .md file
  python DQMapGen.py --stx --from-excel    Convert from Excel file (generates .md and .h)
  python DQMapGen.py --krk                 Krackan uses STX input file'''
        )
        platform_group = parser.add_mutually_exclusive_group(required=True)
        # Rembrandt family
        platform_group.add_argument('--rmb', action='store_const', const='rmb', dest='platform',
                                  help='Use Rembrandt platform configuration')
        # Phoenix family
        platform_group.add_argument('--phx', action='store_const', const='phx', dest='platform',
                                  help='Use Phoenix platform configuration')
        platform_group.add_argument('--hpt', action='store_const', const='hpt', dest='platform',
                                  help='Use Hawkpoint platform configuration (Phoenix family)')
        # Strix family
        platform_group.add_argument('--stx', action='store_const', const='stx', dest='platform',
                                  help='Use Strix platform configuration')
        platform_group.add_argument('--krk', action='store_const', const='krk', dest='platform',
                                  help='Use Krackan platform configuration (Strix family)')
        platform_group.add_argument('--gpt', action='store_const', const='gpt', dest='platform',
                                  help='Use Granite Point platform configuration (Strix family)')

        # Input source option
        parser.add_argument('--from-excel', action='store_true', dest='from_excel',
                          help='Convert from Excel file instead of existing .md file')

        args = parser.parse_args()
        return args

if __name__ == "__main__":

    # Parse command line arguments to get the platform

    data_groups = None
    interactive_offsets = None
    parameters_obtained = False

    args = parse_command_line_args()
    platform = args.platform
    from_excel = args.from_excel

    # --- Step 0: Convert Excel to Markdown if --from-excel is specified
    if from_excel:
        # Get the input_file key for this platform (handles krk/gpt using stx)
        input_file_key = PLATFORM_CONFIGS.get(platform, {}).get('input_file', platform)
        print(f"Converting Excel to Markdown for platform: {input_file_key}")
        if not convert_excel_to_markdown(input_file_key):
            logger.error(f"Failed to convert Excel to Markdown for platform: {input_file_key}")
            sys.exit(1)
        print(f"Excel conversion completed successfully.")

    get_file_name(platform)

    # --- Step 1: Get interactive offsets
    # TODO: use logging instead of print statements
    print("Attempting to get offsets interactively...")
    interactive_offsets = get_offsets_interactively()

    if not interactive_offsets:
        logger.critical("Failed to obtain valid offsets interactively. Program cannot continue.")
        sys.exit(1)
    else:
        logger.info("Successfully obtained user offsets interactively: %s", interactive_offsets)
        flattened_offsets = list(itertools.chain.from_iterable(interactive_offsets))
        logger.info("Flattened offsets: %s", flattened_offsets)

    # --- Step 2: Try reading and parsing the file for data_groups --- REQUIRE this to succeed too
    print(f"\nAttempting to read and parse {dqmap_filename} for data groups...")
    success, file_content_or_error = read_dqmap_file(dqmap_filename)

    if success:
        print(f"{dqmap_filename} file content loaded successfully.")
        parsed_data_groups = parse_dqmap_content(file_content_or_error)

        if parsed_data_groups is not None:
            logger.info(f"Successfully parsed data groups from {dqmap_filename}.")
            data_groups = parsed_data_groups
            parameters_obtained = True
        else:
            logger.error(f"Could not parse necessary data_groups from {dqmap_filename}.")
            parameters_obtained = False
    else:
        logger.error(f"Error reading file: {file_content_or_error}")
        logger.error(f"Cannot proceed without {dqmap_filename} file.")
        parameters_obtained = False

    # --- Step 3: Proceed only if BOTH interactive offsets AND data groups were obtained ---
    if parameters_obtained:
        # TODO: out put the generated groups to a a header file.
        # TODO: determine the header file format by APU etc. RMB/HPT/STX
        logger.info(f"\nGenerating MEM data groups using interactive offsets and data groups from {dqmap_filename}...")
        groups = generate_mem_data_groups(flattened_offsets, data_groups)
        if groups:
            logger.info("\n--- Generated MEM Data Groups Matrix ---")
            for i, group in enumerate(groups):
                logger.info(f"Group {i+1}: {{ {', '.join(group)} }}")
            logger.info("--- End of Matrix ---\n")

            input_basename = os.path.basename(dqmap_filename)
            output_name = f"dqmap_{platform}.h"
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

            os.makedirs(output_path, exist_ok=True)
            output_file = os.path.join(output_path, output_name)

            # TODO: rewrite with creating a helper function to generate the output file
            with open(output_file, 'w') as f:
                f.write(f"// Auto-generated DQ Map for {PLATFORM_CONFIGS[platform]['name']}\n")
                f.write("// Generated by DQMapGen.py\n\n")
                f.write("#ifndef DQMAP_H\n")
                f.write("#define DQMAP_H\n\n")
                f.write(f"// Format: {PLATFORM_CONFIGS[platform]['header_format']}\n")
                f.write(f"// Pattern: {PLATFORM_CONFIGS[platform]['data_pattern']}\n\n")
                f.write("const char* dq_map[][8] = {\n")
                # MA/MB Mapping block (groups 0-7)
                f.write("  // MA/MB Mapping\n")
                f.write("  {\n")
                f.write("    // MAA/MAB\n")
                for group in groups[0:4]:
                    f.write(f"    {{ {', '.join(group)} }},\n")
                f.write("    // MBA/MBB\n")
                for group in groups[4:8]:
                    f.write(f"    {{ {', '.join(group)} }},\n")
                f.write("  },\n")
                # MC/MD Mapping block (groups 8-15)
                f.write("  // MC/MD Mapping\n")
                f.write("  {\n")
                f.write("    // MCA/MCB\n")
                for group in groups[8:12]:
                    f.write(f"    {{ {', '.join(group)} }},\n")
                f.write("    // MDA/MDB\n")
                for group in groups[12:16]:
                    f.write(f"    {{ {', '.join(group)} }},\n")
                f.write("  }\n")
                f.write("};\n\n")
                f.write("#endif // DQMAP_H\n")

            logger.info(f"DQ Map matrix successfully saved to: {output_file}")
        else:
            logger.error("Generation of MEM data groups failed.")

    else:
        # This block is reached if interactive offsets failed, file wasn't found, OR parsing failed.
        logger.error(f"Could not obtain necessary parameters (interactive offsets and/or data groups from {dqmap_filename}). Program terminated.")
        sys.exit(1)

