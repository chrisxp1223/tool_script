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


def read_dqmap_file():
    """
    Check if dqmap.md exists and read its contents.
    
    Returns:
        tuple: (bool, str) - (success status, file contents or error message)
    """
    try:
        file_path = "dqmap.md"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"Error: {file_path} not found"
            
        # Read file contents
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        if not content:
            return False, f"Error: {file_path} is empty"
        
                # --- Print the content if successfully read ---
        print("\n--- Content of dqmap.md ---")
        print(content)
        print("--- End of dqmap.md Content ---\n")
        # ---------------------------------------------

        # Return True and the content
        return True, content
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def parse_dqmap_content(content):
    """
    Parses the content of the dqmap.md file to extract offsets and data groups.

    Args:
        content (str): The content read from the dqmap.md file.

    Returns:
        tuple: (list, list) - A tuple containing the list of offsets and the list
               of data groups. Returns (None, None) if parsing fails.
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
            # Identify which section we're in
            if "[7:0] Lower Byte Group" in line and "B Side" not in line:
                current_section = "lower"
                is_b_side = False
            elif "[15:8] Upper Byte Group" in line and "B Side" not in line:
                current_section = "upper"
                is_b_side = False
            elif "[7:0] Lower Byte Group (B Side)" in line:
                current_section = "lower"
                is_b_side = True
            elif "[15:8] Upper Byte Group (B Side)" in line:
                current_section = "upper"
                is_b_side = True
            
            # Skip header rows and empty lines
            if line.startswith('|') and "DRAM DQ Lane" not in line and "---" not in line:
                # Parse the table row
                parts = line.split('|')
                if len(parts) >= 6:  # Ensure valid row format
                    # Extract DQ lane number
                    dq_lane = int(parts[1].strip().replace("DQ", ""))
                    
                    # Extract pin numbers for each channel
                    channel_a_pin = int(parts[2].strip())
                    channel_b_pin = int(parts[3].strip())
                    channel_c_pin = int(parts[4].strip())
                    channel_d_pin = int(parts[5].strip())
                    
                    # Store in the appropriate section and side
                    if not is_b_side:  # A side
                        if current_section == "lower":
                            mapping['MAA']['lower'][dq_lane] = channel_a_pin
                            mapping['MBA']['lower'][dq_lane] = channel_b_pin
                            mapping['MCA']['lower'][dq_lane] = channel_c_pin
                            mapping['MDA']['lower'][dq_lane] = channel_d_pin
                        else:  # upper
                            mapping['MAA']['upper'][dq_lane-8] = channel_a_pin
                            mapping['MBA']['upper'][dq_lane-8] = channel_b_pin
                            mapping['MCA']['upper'][dq_lane-8] = channel_c_pin
                            mapping['MDA']['upper'][dq_lane-8] = channel_d_pin
                    else:  # B side
                        if current_section == "lower":
                            mapping['MAB']['lower'][dq_lane] = channel_a_pin
                            mapping['MBB']['lower'][dq_lane] = channel_b_pin
                            mapping['MCB']['lower'][dq_lane] = channel_c_pin
                            mapping['MDB']['lower'][dq_lane] = channel_d_pin
                        else:  # upper
                            mapping['MAB']['upper'][dq_lane-8] = channel_a_pin
                            mapping['MBB']['upper'][dq_lane-8] = channel_b_pin
                            mapping['MCB']['upper'][dq_lane-8] = channel_c_pin
                            mapping['MDB']['upper'][dq_lane-8] = channel_d_pin
        
        # Default offsets (these should be configured based on your specific needs)
        # For example: offsets for MAA, MAB, MBA, MBB, etc.
        offsets = [16, 24, 0, 8, 16, 24, 0, 8, 16, 24, 0, 8, 16, 24, 0, 8]
        
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
        
        return offsets, data_groups
        
    except Exception as e:
        print(f"Error parsing dqmap.md content: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def generate_mem_data_groups(offsets, data_groups):
    result = []

    for offset, group in zip(offsets, data_groups):
        processed_group = []
        for num in group:
            # Apply rule: subtract 8 if num > 8
            if num >= 8:
                num -= 8
            # Add offset and format
            value = num + offset
            processed_group.append(f"MEM_MX_DATA_{value:02d}")
        result.append(processed_group)

    return result

def get_user_input():
    try:
        # Get offsets
        print("Enter 4 offset values (space-separated, e.g., '16 24 0 8'):")
        offsets = list(map(int, input().strip().split()))
        if len(offsets) != 4:
            raise ValueError("Must enter exactly 4 offset values")

        # Get data groups
        data_groups = []
        print("\nEnter 4 groups of 8 numbers (space-separated)")
        print("Enter one group per line:")
        for i in range(4):
            group = list(map(int, input().strip().split()))
            if len(group) != 8:
                raise ValueError(f"Group {i+1} must contain exactly 8 numbers")
            data_groups.append(group)

        return offsets, data_groups

    except ValueError as e:
        print(f"Error: {e}")
        return None, None

if __name__ == "__main__":
    offsets = None
    data_groups = None
    parameters_obtained = False # Flag to track if we got parameters

    # Try reading the file first
    success, file_content_or_error = read_dqmap_file()

    if success:
        # File was read successfully. Content is in file_content_or_error
        print("dqmap.md file content loaded successfully.")
        # Attempt to parse the content
        offsets, data_groups = parse_dqmap_content(file_content_or_error)

        if offsets is not None and data_groups is not None:
            print("Successfully parsed parameters from dqmap.md.")
            parameters_obtained = True
        else:
            # Parsing failed or not implemented, fall back to manual input
            print("Could not parse parameters from dqmap.md. Please provide parameters manually.")
            offsets, data_groups = get_user_input()
            if offsets is not None and data_groups is not None:
                parameters_obtained = True
    else:
        # File reading failed (not found or empty)
        print(file_content_or_error) # Print the specific error from read_dqmap_file
        print("Attempting to get parameters via manual input.")
        offsets, data_groups = get_user_input()
        if offsets is not None and data_groups is not None:
            parameters_obtained = True # Got parameters from user


    # Proceed only if parameters were obtained (either from file parsing OR user input)
    if parameters_obtained:
        print("\nGenerating MEM data groups...")
        groups = generate_mem_data_groups(offsets, data_groups)
        for group in groups:
            print("{ " + ", ".join(group) + " },\n")
    else:
        # This block is reached if file wasn't found AND user input failed/was cancelled,
        # OR if file WAS found but parsing failed (once implemented) AND subsequent user input failed.
        print("Could not obtain necessary parameters. Program terminated.")
        exit(1)