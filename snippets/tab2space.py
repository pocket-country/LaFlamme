import sys
import os

def convert_tabs_to_spaces(filepath, space_count=4):
    """
    Scans a source file and replaces every tab character with a specified 
    number of spaces (default is 4, which is Python standard).
    
    This function overwrites the original file with the corrected content.
    """
    # 1. Check if the file exists
    if not os.path.exists(filepath):
        print(f"\n\033[91mError:\033[0m File not found at '{filepath}'")
        return

    # 2. Read the entire content of the file
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"\n\033[91mError:\033[0m Could not read file: {e}")
        return

    # 3. Perform the replacement
    space_replacement = ' ' * space_count
    # The string method .replace() is highly efficient for this task.
    new_content = content.replace('\t', space_replacement)

    # Check if any change was actually made
    if content == new_content:
        print(f"\n\033[93mWarning:\033[0m No tabs found in '{filepath}'. File remains unchanged.")
        return

    # 4. Write the modified content back to the original file
    try:
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        # 5. Success message with ANSI color
        green_check = '\033[92m\u2705\033[0m' 
        print(f"\n{green_check} Success! Indentation in '{filepath}' standardized.")
        print(f"   Replaced all tabs with {space_count} spaces.")

    except Exception as e:
        print(f"\n\033[91mError:\033[0m Could not write to file: {e}")


if __name__ == '__main__':
    # Check if a filename was provided as a command-line argument
    if len(sys.argv) < 2:
        print("\nUsage: python tab_to_space_converter.py <filename>")
        print("Example: python tab_to_space_converter.py Pedro.py")
        sys.exit(1)

    input_file = sys.argv[1]
    convert_tabs_to_spaces(input_file)
