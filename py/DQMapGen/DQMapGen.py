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
import os
import sys # Import the sys module for exiting on error
import itertools # Import itertools for flattening lists


def read_dqmap_file(file_path):
    """
    Check if a given file exists and read its contents.

    Args:
        file_path (str): The path to the dqmap file to read.

    Returns:
        tuple: (bool, str) - (success status, file contents or error message)
    """
    try:
        # Use the provided file_path argument
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"Error: File not found at {file_path}"

        # Read file contents
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if not content:
            return False, f"Error: File is empty at {file_path}"

        # --- Print the content if successfully read ---
        print(f"\n--- Content of {os.path.basename(file_path)} ---") # Use basename for cleaner print
        print(content)
        print(f"--- End of {os.path.basename(file_path)} Content ---\n")
        # ---------------------------------------------

        # Return True and the content
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
                print(f"Section: {current_section}, B side: {is_b_side}")
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
    for channel_idx in range(4):  # 4 channels: MA, MB, MC, MD
        # Get the base offsets for this channel (4 offsets per channel)
        channel_offsets = offsets[channel_idx * 4:(channel_idx + 1) * 4]

        # Process A-side lower byte group
        a_lower_group = []
        a_data = data_groups[channel_idx * 4]  # Get A-side lower byte data
        for dq_idx, pin in enumerate(a_data):
            # Determine which offset to use (0-7 maps to first offset)
            offset = channel_offsets[0]  # Use first offset for lower byte
            value = pin
            if value >= 8:
                value -= 8
            value += offset
            a_lower_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(a_lower_group)

        # Process A-side upper byte group
        a_upper_group = []
        a_data = data_groups[channel_idx * 4 + 1]  # Get A-side upper byte data
        for dq_idx, pin in enumerate(a_data):
            # Determine which offset to use (8-15 maps to second offset)
            offset = channel_offsets[1]  # Use second offset for upper byte
            value = pin
            if value >= 8:
                value -= 8
            value += offset
            a_upper_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(a_upper_group)

        # Process B-side lower byte group
        b_lower_group = []
        for dq_idx in range(8):
            # Use third offset for B-side lower byte
            offset = channel_offsets[2]
            value = dq_idx + offset
            b_lower_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(b_lower_group)

        # Process B-side upper byte group
        b_upper_group = []
        for dq_idx in range(8):
            # Use fourth offset for B-side upper byte
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
        print("\nOperation interrupted. Exiting.")
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
                print("\nOperation interrupted. Exiting.")
                sys.exit(1)

        all_offset_groups.append(current_channel_offsets)

    return all_offset_groups

if __name__ == "__main__":

    # TODO: Add argument parsing for dqmap_filename
    dqmap_filename = "dqmap_rmb.md" # Define the filename variable here

    data_groups = None
    interactive_offsets = None
    parameters_obtained = False

    # --- Step 1: Get interactive offsets --- REQUIRE this to succeed
    # TODO: use logging instead of print statements
    print("Attempting to get offsets interactively...")
    interactive_offsets = get_offsets_interactively()

    if not interactive_offsets:
        # Function should exit on failure, but handle defensively
        print("Error: Failed to obtain valid offsets interactively. Program cannot continue.")
        sys.exit(1)
    else:
        print("\nSuccessfully obtained user offsets interactively:")
        print(interactive_offsets)
        # Flatten the interactive_offsets into a single list
        flattened_offsets = list(itertools.chain.from_iterable(interactive_offsets))
        print("\nFlattened offsets:")
        print(flattened_offsets)

    # --- Step 2: Try reading and parsing the file for data_groups --- REQUIRE this to succeed too
    print(f"\nAttempting to read and parse {dqmap_filename} for data groups...")
    success, file_content_or_error = read_dqmap_file(dqmap_filename)

    if success:
        print(f"{dqmap_filename} file content loaded successfully.")
        # Attempt to parse the content - Now only returns data_groups or None
        parsed_data_groups = parse_dqmap_content(file_content_or_error)

        # Check if parsing was successful (got data_groups)
        if parsed_data_groups is not None:
            print(f"Successfully parsed data groups from {dqmap_filename}.")
            data_groups = parsed_data_groups # Assign the successfully parsed groups
            parameters_obtained = True # We have both interactive_offsets and data_groups
        else:
            # Parsing failed
            print(f"Error: Could not parse necessary data_groups from {dqmap_filename}.")
            parameters_obtained = False
    else:
        # File reading failed
        print(f"Error reading file: {file_content_or_error}")
        print(f"Cannot proceed without {dqmap_filename} file.")
        parameters_obtained = False

    # --- Step 3: Proceed only if BOTH interactive offsets AND data groups were obtained ---
    if parameters_obtained:
        print(f"\nGenerating MEM data groups using interactive offsets and data groups from {dqmap_filename}...")
        # Pass the FLATTENED offsets and the parsed data_groups
        groups = generate_mem_data_groups(flattened_offsets, data_groups)
        if groups: # Check if generation was successful
            for group in groups:
                print("{ " + ", ".join(group) + " },\n")
        else:
            print("Generation of MEM data groups failed.")
    else:
        # This block is reached if interactive offsets failed, file wasn't found, OR parsing failed.
        print(f"\nCould not obtain necessary parameters (interactive offsets and/or data groups from {dqmap_filename}). Program terminated.")
        sys.exit(1) # Exit with an error status

    # TODO: determine the header file format by APU etc. RMB/HPT/STX
    # TODO: out put the generated groups to a a header file.
