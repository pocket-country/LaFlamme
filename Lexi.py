from StrucDef import Token, TokenType, CharacterStream
import sys
import os
from typing import List, Optional

# Helper function to consume a known sequence of characters
def consume_sequence(stream: CharacterStream, length: int) -> str:
    """Consumes the next 'length' characters from the stream."""
    sequence = ""
    for _ in range(length):
        char = stream.next_char()
        if char is None:
            # Should not happen if peek was correct, but handles EOF gracefully
            return sequence
        sequence += char
    return sequence

def get_next_token(stream: CharacterStream) -> Token:
    """
    Identifies and returns the next Token from the stream.
    This function relies heavily on peek() to check for multi-character delimiters 
    before committing to consumption.
    """
    start_line = stream.line
    start_column = stream.column
    
    # 1. Skip non-delimiter whitespace (Spaces and Tabs)
    while True:
        char = stream.peek()
        if char is None:
            return Token(TokenType.EOF, "", stream.line, stream.column)
        
        # NOTE: Newlines are NOT skipped here; they are tokenized (see step 2)
        if char == ' ' or char == '\t':
            stream.next_char() # Consume the space/tab
        else:
            break

    # Re-evaluate position after skipping whitespace
    start_line = stream.line
    start_column = stream.column
    
    # 2. Check for single and multi-character delimiters/tokens
    
    # Check for EOF again after skipping whitespace
    if stream.peek() is None:
        return Token(TokenType.EOF, "", stream.line, stream.column)
    
    # Single-character lookups are simplest
    char1 = stream.peek(1)

    if char1 == "'":
        stream.next_char()
        return Token(TokenType.SINGLE_QUOTE, "'", start_line, start_column)
    
    if char1 == ";":
        stream.next_char()
        return Token(TokenType.END_STATEMENT, ";", start_line, start_column)

    # Multi-character lookups require peek(2)
    char2 = stream.peek(2)
    
    # Block Comment Start: /*
    if char1 == '/' and char2 == '*':
        value = consume_sequence(stream, 2)
        return Token(TokenType.START_BLOCK_COMMENT, value, start_line, start_column)
    
    # Block Comment End: */
    if char1 == '*' and char2 == '/':
        value = consume_sequence(stream, 2)
        return Token(TokenType.END_BLOCK_COMMENT, value, start_line, start_column)

    # Line Comment Start: --
    if char1 == '-' and char2 == '-':
        value = consume_sequence(stream, 2)
        return Token(TokenType.START_LINE_COMMENT, value, start_line, start_column)

    # Newline Token (Must be checked after all other delimiters)
    if char1 == '\n':
        stream.next_char()
        # The raw value is '\n', but the PDA uses the TokenType
        return Token(TokenType.NEWLINE, '\n', start_line, start_column)

    # 3. If it's not a delimiter, it's a CONTENT_CHUNK
    
    chunk_value = ""
    
    # Consume the first character of the chunk
    chunk_value += stream.next_char() 

    # Loop to consume all subsequent characters until the start of ANY delimiter
    while True:
        char1 = stream.peek(1)
        char2 = stream.peek(2)
        
        if char1 is None:
            break # EOF
        
        # Check if the next character(s) start any of our defined tokens
        is_delimiter_start = (
            char1 in ["'", ";", '\n'] or
            (char1 == '/' and char2 == '*') or
            (char1 == '*' and char2 == '/') or
            (char1 == '-' and char2 == '-')
        )
        
        if is_delimiter_start:
            break # Stop consuming content chunk right before the delimiter starts
            
        # If it's not a delimiter, consume it and append to the chunk
        chunk_value += stream.next_char()

    return Token(TokenType.CONTENT_CHUNK, chunk_value, start_line, start_column)

# --- Standalone Execution Logic ---

def tokenize_file_to_output(input_filename: str, output_filename: str):
    """Reads input file, tokenizes content, and writes tokens to output file."""
    
    # 1. Read entire input file content
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # 2. Tokenize the content
    stream = CharacterStream(source_code)
    tokens: List[Token] = []
    
    while True:
        token = get_next_token(stream)
        tokens.append(token)
        if token.type == TokenType.EOF:
            break
            
    # 3. Write tokens to the output file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            for token in tokens:
                f.write(token.to_test_line() + '\n')
        print(f"Successfully tokenized '{input_filename}' to '{output_filename}'")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == '__main__':
    # Usage: python Lexi.py <input_file>
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <input_file.sql>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    
    # Determine output filename (x.sql -> x.tok)
    base_name, ext = os.path.splitext(input_filename)
    output_filename = base_name + '.tok'
    
    tokenize_file_to_output(input_filename, output_filename)
