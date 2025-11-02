# File Parser.py -- uses Lexi and Pedro to parse a file.
# I think this one is just a bunch of functions, shouldn't define any data structures

# code from Pedro main execution block

# --- Main Execution Block ---

def parse_file(input_file_path: str, mode = 'verbose'):
    """Tokenizes and then parses the input file."""

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

    if mode == 'verbose':
        print(f"Running parser on {input_file_path}\n")

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

    if mode == 'verbose':
        print(f"Lexi OK, tokens in {token_filename}\n")

    # Parsing Phase
    # instantiate parser class, load in tokens ... 
    parser = PDA(pda.PDA_TRANSITIONS)
    parser.set_token_list(tokens)

    # and run ...
    if mode == 'verbose':
        print(f"Starting PDA run ...")
    is_accepted = parser.run(mode)

    if is_accepted:
        return TestStatus.PASSED
    else:
        return TestStatus.FAILED
