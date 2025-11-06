# A test harness for the PDA/Pedro.py
import os
import sys
from typing import List
import re

from Constants import TestStatus
import Constants as C

# imports needed by Pedro.py
from StructDef import Token, CharacterStream
import StructDef as tt
import ParseDef

import Pedro #the PDA/Parser class & associated data

def main():
    # Test files are are all named ./tests/testDD.sql and contain valid SQL so should be accepted by parser
    # TODO set up to handle/test for "fail" cases (an expected result dict, ...)
 
    # Setup
    TEST_DIR = "tests"
    TEST_DIR = "./tests"
    SQL_PATTERN = r'test\d{2}\.sql'

    LABEL_FILE_PATH = "./tests/testDescriptions.txt" 
    DIGIT_EXTRACTOR = r'test(\d{2})\.sql' 
    test_desc = {}
    
    # load test descriptions link using digits in filename
    with open(LABEL_FILE_PATH, 'r') as f:
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
        
        input_filename = os.path.basename(full_path)      
        
        match = re.search(DIGIT_EXTRACTOR, input_filename)
        if match:
            test_id = match.group(1) 
            desc = test_desc.get(test_id, "No description available") 
  !!!! stopped here.  think through overall structure, ?? set up single file parser shell??    


perverted PS shell --
# Assumes you pass the arguments (e.g., .\tests\test01.sql) directly
$args = $args -join ' '  # Rejoin arguments if they are split
python -m support.Pedro $args  
---
        #run the parse process & check result
        result = Pedro.parse_file(full_path, mode = 'silent')
        
        match result:
            case TestStatus.PASSED:
                passed_count += 1
                print(f"{C.SYMBOL_PASS} File {input_filename}/ {desc} accepted")
            case TestStatus.FAILED:
                print(f"{C.SYMBOL_FAIL} File {input_filename}/ {desc} contained a syntax error.")
            case TestStatus.FILE_ERROR:
                print(f"{C.SYMBOL_ERROR} File I/O Error")
            
    print(f"\n Results: {passed_count}/{total_tests} Tests Passed ---\n")
    
    # note return code logic opposit of boolean
    if passed_count == total_tests:
        return 0
    else:
        return 1

if __name__ == "__main__":
        
    sys.exit(main())
