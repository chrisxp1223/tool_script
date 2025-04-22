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
                 of data groups. Returns (None, None) if parsing fails or is
                 not implemented yet.
    """
    # TODO: Implement the actual parsing logic here.
    # This is a placeholder implementation.
    print("Parsing dqmap.md content...")
    # Example: Look for specific patterns or tables in the markdown content.
    # For now, it just returns None, None to indicate parsing is not done.
    offsets = None
    data_groups = None
    print("Parsing logic not yet implemented.")
    return offsets, data_groups

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