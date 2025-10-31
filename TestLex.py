import os
import filecmp
from typing import List
from datastructures import CharacterStream, tokenize # Import the core logic

def run_test(input_file_path: str, expected_file_path: str) -> bool:
    """
    Runs the lexer on the input file and compares the token output 
    to the expected output file.
    """
    # 1. Lex the Input
    try:
        stream = CharacterStream(input_file_path)
        tokens = tokenize(stream)
    except Exception as e:
        print(f"  FAILED (Exception during Lexing): {e}")
        return False

    # 2. Write the Generated Output to a temporary file
    temp_output_path = input_file_path + ".temp_out"
    with open(temp_output_path, 'w', encoding='utf-8') as f:
        for token in tokens:
            f.write(token.to_test_line() + '\n')

    # 3. Compare Generated Output with Expected Output
    is_same = False
    try:
        # Simple file comparison
        is_same = filecmp.cmp(temp_output_path, expected_file_path, shallow=False)
        
        if not is_same:
            print("  FAILED (Output Mismatch)")
            # In a real environment, you'd call a diff tool here (like 'diff')
            
    finally:
        # Clean up the temporary file
        os.remove(temp_output_path)
        
    return is_same

def main():
    # --- Setup ---
    TEST_DIR = "tests"
    
    if not os.path.isdir(TEST_DIR):
        print(f"Test directory '{TEST_DIR}' not found. Please create it.")
        return

    # Find all test input files (.in)
    test_files = [f for f in os.listdir(TEST_DIR) if f.endswith(".sql")]
    
    if not test_files:
        print(f"No '.in' files found in '{TEST_DIR}'.")
        return

    total_tests = len(test_files)
    passed_count = 0
    
    print(f"\n--- Running Lexer Tests ({total_tests} cases found) ---\n")

    for input_filename in sorted(test_files):
        print(f"Running: {input_filename}")
        
        input_path = os.path.join(TEST_DIR, input_filename)
        expected_filename = input_filename.replace(".in", ".val")
        expected_path = os.path.join(TEST_DIR, expected_filename)
        
        if not os.path.exists(expected_path):
            print(f"  SKIPPED: Missing expected output file '{expected_filename}'")
            continue

        if run_test(input_path, expected_path):
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
