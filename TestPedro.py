# A test harness for the PDA/Pedro.py
import os
import read
from typing import List
from datastructures import CharacterStream, tokenize

def run_test(input_file_path: str) -> bool:
    """
    Runs the parser function on the input file and see if it is accepted 
    (by checking return value)
    """
    if parse_file(input_filename):
            print(f"\u2705 File {input_filename} accepted")
        else:
            print(f"\u274C File {input_filename} contained a syntax error.")

def main():
    # --- Setup ---
    TEST_DIR = "tests"
    
    if not os.path.isdir(TEST_DIR):
        print(f"Test directory '{TEST_DIR}' not found. Please create it.")
        return

    # Find all test input files.  These are all named testDD.sql and contain valid SQL so should be accepted by parser
    # TODO set up to handle/test "fail" cases
    TEST_DIR = "your/test/directory/path"
    SQL_PATTERN = r'Test\d{2}\.sql'

    # List comprehension: Filter for actual files that match the regex pattern
    # NOTE: We are storing the full path, NOT just the filename.
    test_files = [
        os.path.join(TEST_DIR, f) 
        for f in os.listdir(TEST_DIR) 
        if re.fullmatch(SQL_PATTERN, f) and os.path.isfile(os.path.join(TEST_DIR, f))
    ]   
    if not test_files:
        print(f"No 'TestNN.sql' files found in '{TEST_DIR}'.")
        return

    total_tests = len(test_files)
    passed_count = 0

    # See if we have a test info/label file
    test_labels = {}
    LABEL_FILE_PATH = "path/to/your/labels.txt" 
    with open(label_file_path, 'r') as f:
        for line in f:
            # Split at the first space
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                # Key is the digit string, value is the rest of the line (the label)
                test_labels[parts[0]] = parts[1]

    print(f"\n--- Running Syntax Acceptance Tests ({total_tests} cases found) ---\n")

    # The pattern with a CAPTURING GROUP around the digits
    DIGIT_EXTRACTOR = r'Test(\d{2})\.sql' 

    for full_path in test_files:
        # 1. Get just the filename from the full path
        filename = os.path.basename(full_path)
        
        # 2. Use re.search to find the pattern and extract the captured group (the digits)
        match = re.search(DIGIT_EXTRACTOR, filename)
        
        if match:
            # The digits (e.g., '05') are in the first captured group (index 1)
            test_id = match.group(1) 
            
            # 3. Look up the label
        label = test_label_map.get(test_id, "Label Not Found") 
		
		# --- Execute your test code here ---
    for input_filename in sorted(test_files):
        print(f"Running: {input_filename}")
        
        input_path = os.path.join(TEST_DIR, input_filename)
        expected_filename = input_filename.replace(".in", ".val")
        expected_path = os.path.join(TEST_DIR, expected_filename)
        
        if not os.path.exists(expected_path):
            print(f"  SKIPPED: Missing expected output file '{expected_filename}'")
            continue

        if run_test(input_path):
            print("  PASSED")
            passed_count += 1
        
    print(f"\n--- Results: {passed_count}/{total_tests} Tests Passed ---\n")
    if passed_count < total_tests:
        print("ACTION REQUIRED: Check the output files against the expected files to see the mismatch.")


if __name__ == "__main__":
    # Ensure the test_cases directory exists before running
    if not os.path.exists('tests'):
        os.makedirs('test_cases')
        print("Created 'test_cases' directory. Add your .in and .out files there.")
        
    # Create a simple initial test case for demonstration
    with open('test_cases/01_basic.in', 'w') as f:
        f.write("SELECT A FROM B; -- Line comment\n SELECT C;")
        
    with open('test_cases/01_basic.out', 'w') as f:
        # This is the expected tokenized output based on the lexer logic
        f.write("[1:1] CODE_TEXT: \"SELECT A FROM B\"\n")
        f.write("[1:17] END_STATEMENT: \";\"\n")
        f.write("[1:19] START_LINE_COMMENT: \"--\"\n")
        f.write("[1:22] COMMENT_TEXT: \" Line comment\"\n")
        f.write("[1:34] NEWLINE: \"\\n\"\n")
        f.write("[2:2] CODE_TEXT: \"SELECT C\"\n")
        f.write("[2:10] END_STATEMENT: \";\"\n")
        f.write("[2:11] EOF: \"\"\n")
        
    main()
