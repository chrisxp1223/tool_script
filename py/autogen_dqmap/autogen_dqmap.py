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

# User input excle file thne read the file
# 1. excel file reading check
#  - check the file is readable
#  - check the is the file inculded nassary columns
#  - check the data is valid


# 2. validation base function
#  - check the if there any data is lost
#  - check the if the namming is matched the requirement
#  - check the pin number is in the avaliable range


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
    offsets, data_groups = get_user_input()
    
    if offsets is None or data_groups is None:
        print("Invalid input. Program terminated.")
        exit(1)

    groups = generate_mem_data_groups(offsets, data_groups)

    for group in groups:
        print("{ " + ", ".join(group) + " },\n")
