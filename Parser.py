# File Parser.py -- uses Lexi and Pedro to parse a file.
# I think this one is just a bunch of functions, shouldn't define any data structures
# This sorts out file IO, calls the Lexi and Pedro (PDA) run methods and 
# contains a boatload of code setting up for instrumentation
import os
import datetime
import hashlib
import json
from enum import Enum

# --- Configuration (Centralized Settings) ---
# NOTE: Assume you pass the TestStatus Enum from status_config.py
LOG_FILE_PATH = 'run_log.txt'
TEST_PASS_STATUS = 'PASSED' # Use string representation for logging clarity

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARSER_DEF = os.path.join(SCRIPT_DIR, "ParseDef.py")
DEFINITION_STORE = "parser_defs"

def hash_parser_def(file_content: str) -> str:
    """
    Generates a stable SHA-256 hash for the parser definition file
    (constant defs representing various alphabets, transition rules)
    
    The parser definition file is currently stored in ParseDef.py in the 
    directory the parser script is run from (i.e from where it is imported.
    
    Returns:
        str: The SHA-256 hash.
    """
    hasher = hashlib.sha256()
    hasher.update(file_content.encode('utf-8')
    return hasher.hexdigest()
   

def append_run_log(source_id, transition_dict, final_status: Enum, final_trace):
    """
    Appends a new record to the run log file for each transaction executed by the PDA
    """
    
    # 1. Calculate the Hash and Save the Snapshot
    ruleset_hash = calculate_ruleset_hash(transition_dict)
    save_ruleset_snapshot(ruleset_hash, transition_dict)
    
    # 2. Format Log Line Components
    timestamp = datetime.datetime.now().isoformat()
    
    # Convert the Enum to a clean string for the log
    status_str = final_status.name 
    
    # Convert the trace list to a stable string representation
    trace_str = repr(final_trace)
    
    # 3. Create the Log Record
    log_record = f"{timestamp}|{source_id}|{ruleset_hash}|{status_str}|{trace_str}\n"

    # 4. Append to the Log File
    try:
        with open(LOG_FILE_PATH, 'a') as f:
            f.write(log_record)
        
        # print(f"[Trace] Logged run {source_id} (Status: {status_str})")
    except Exception as e:
        print(f"\n[Trace ERROR] Could not append to run log: {e}")


class PDARunTrace:
    """
    A simple class to hold the transition trace for a single parser run.
    (now with added write to log power)
    """
    def __init__(self):
        # Stores tuples: (trigger_key, action_value, success_flag)
        self.trace_buffer = []

    def record_transition(self, trigger_key, action_value, success=True):
        """Records a single transition (real or ghost) to the buffer."""
        # Ensure trigger_key is represented as a string for storage
        trigger_str = str(trigger_key) 
        
        if success:
            status = "Next"
            normalized_action = _normalize_action_value(action_value)
        else:
            status = "Fail"
            normalized_action = action_value
            
        self.trace_buffer.append({
            'trigger': trigger_str,
            'action': normalized_action,
            'result': status
        })
        
    def get_log_data(self):
        """Returns the complete, current trace buffer."""
        return self.trace_buffer

# code from Pedro main execution block
# --- Main Execution Block ---

def parse_file(input_file_path: str, verbose = True):
    """Tokenizes and then parses the input file."""
    
    # Save definitions - as file is used in imports we assume it exists cause code hasn't crashed
    with open(PARSER_DEF, 'r') as f:
        # ... read the file ...    
        parser_definition = f.read()
    
    definition_ID = hash_parser_def(parser_definition)
    definition_file = os.path.join(SCRIPT_DIR, DEFINITION_STORE, f"{definition_ID}.py") 

    if not(os.path.exists(definition_file)):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)

hit the wall here, 3am!
need to set up logging class.  
do I keep it in this file or put in struct def?




    # Lexing Phase
    try:
        from Lexi import get_next_token # Import the lexer function

        # Read file content
        with open(input_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file_path}")
        return TestStatus.FILE_ERROR
    except ImportError:
        print("Error: Could not import Lexi. Please ensure 'Lexi.py' is in the same directory.")
        return TestStatus.FILE_ERROR

    if verbose: print(f"Running parser on {input_file_path}\n")

    # Iterate, buidling a token list
    stream = CharacterStream(source_code)
    tokens: List[Token] = []
    while True:
        token = get_next_token(stream)
        tokens.append(token)
        if token.ttype == tt.EOF:
            break

    # for diagnostics, write token list to a file
    base_name, ext = os.path.splitext(input_file_path)
    token_filename = base_name + '.tok'

    try:
        with open(token_filename, 'w', encoding='utf-8') as f:
            for token in tokens:
                f.write(token.to_test_line() + '\n')

    except Exception as e:
        print(f"Error in token output file: {e}")
        return TestStatus.FILE_ERROR

    if verbose' print(f"Lexi OK, tokens in {token_filename}\n")

    # Parsing Phase
    # instantiate parser class, load in tokens ... 
    parser = PDA(pda.PDA_TRANSITIONS)
    parser.set_token_list(tokens)

    # and run ...
    if verbose: print(f"Starting PDA run ...")
    
    is_accepted = parser.run(mode)
    if is_accepted:
        return TestStatus.PASSED
    else:
        return TestStatus.FAILED
