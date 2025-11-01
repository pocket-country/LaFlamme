# A test harness for the PDA/Pedro.py
import os
import read
from typing import List
from datastructures import CharacterStream, tokenize

def main():
    # Test files are are all named ./tests/testDD.sql and contain valid SQL so should be accepted by parser
    # TODO set up to handle/test for "fail" cases (an expected result dict, ...)
 
    # Setup
    TEST_DIR = "tests"
    TEST_DIR = "./tests"
    SQL_PATTERN = r'Test\d{2}\.sql'

    LABEL_FILE_PATH = "./tests/testDescriptions.txt" 
    DIGIT_EXTRACTOR = r'Test(\d{2})\.sql' 
    test_desc = {}
    
    # load test descriptions link using digits in filename
    with open(label_file_path, 'r') as f:
        for line in f:
            # Split at the first space
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                # Key is the digit string, value is the rest of the line (the label)
                test_desc[parts[0]] = parts[1]

    if not os.path.isdir(TEST_DIR):
        print(f"Test directory '{TEST_DIR}' not found.")
        return

    # Find test files (useing list comprehension & regex matck).  Store full path
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

    # get test id for description & run parser for each file
    print(f"\n--- Running Parser Syntax Acceptance Tests. ({total_tests} cases found) ---\n")

    for full_path in test_files:
        filename = os.path.basename(full_path)      
        
        match = re.search(DIGIT_EXTRACTOR, filename)
        if match:
            test_id = match.group(1) 
            desc = test_desc.get(test_id, "No description available") 
            
        if parse_file(input_filename):
            passed_count += 1

            # color = '\033[92m' 
            print(f"\u2705 File {input_filename}/ {desc} accepted")
        else:
            # color ='\033[91m'
            print(f"\u274C File {input_filename}/ {desc} contained a syntax error.")
        
    # color = '\033[0m' # reset
    print(f"\n Results: {passed_count}/{total_tests} Tests Passed ---\n")

if __name__ == "__main__":
        
    main()
