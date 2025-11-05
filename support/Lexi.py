## --- Lexi.py --- 
import sys
import os
from typing import List, Optional

from .StructDef import Token, CharacterStream
from . import ParseDef as tt  # so can access token types as tt.WHATEVER

# --- Lexer class implementation --- 
class Lexer:
    def __init__(self, stream_source):
        
        self.stream = CharacterStream(stream_source)
        self.tokens = []
        
        
    # Internal function to consume a known sequence of characters
    def _consume_sequence(self, stream: CharacterStream, length: int) -> str:
        """Consumes the next 'length' characters from the self.stream."""
        sequence = ""
        for _ in range(length):
            char = self.stream.next_char()
            if char is None:
                # Should not happen if peek was correct, but handles EOF gracefully
                return sequence
            sequence += char
        return sequence

    def _get_next_token(self) -> Token:
        """
        Identifies and returns the next Token from the self.stream.
        This function relies heavily on peek() to check for multi-character delimiters
        before committing to consumption.
        Uses instance variable storing a CharacterStream object

        Note: Token Types defined along with PDA rules in ParseDef.py
        """
        # TODO think about how this handles malformed input.  What is malformed input in this context?
        
        start_line = self.stream.line
        start_column = self.stream.column

        # Skip non-delimiter whitespace (Spaces and Tabs)
        while True:
            char = self.stream.peek()
            if char is None:
                return Token(tt.T_EOF, "", self.stream.line, self.stream.column)

            # NOTE: Newlines are NOT skipped here; they are tokenized (see step 2)
            if char == ' ' or char == '\t':
                self.stream.next_char() # Consume the space/tab
            else:
                break

        # Re-evaluate position after skipping whitespace
        start_line = self.stream.line
        start_column = self.stream.column

        # Check for single and multi-character delimiters/tokens

        # Check for EOF again after skipping whitespace
        if self.stream.peek() is None:
            return Token(tt.T_EOF, "", self.stream.line, self.stream.column)

        # Single-character lookups are simplest
        char1 = self.stream.peek(1)

        if char1 == "'":
            self.stream.next_char()
            return Token(tt.T_SINGLE_QUOTE, "'", start_line, start_column)

        if char1 == ";":
            self.stream.next_char()
            return Token(tt.T_END_STATEMENT, ";", start_line, start_column)

        # Multi-character lookups require peek(2)
        char2 = self.stream.peek(2)

        # Block Comment Start: /*
        if char1 == '/' and char2 == '*':
            value = self._consume_sequence(self.stream, 2)
            return Token(tt.T_START_BLOCK_COMMENT, value, start_line, start_column)

        # Block Comment End: */
        if char1 == '*' and char2 == '/':
            value = self._consume_sequence(self.stream, 2)
            return Token(tt.T_END_BLOCK_COMMENT, value, start_line, start_column)

        # Line Comment Start: --
        if char1 == '-' and char2 == '-':
            value = self._consume_sequence(self.stream, 2)
            return Token(tt.T_START_LINE_COMMENT, value, start_line, start_column)

        # Newline Token (Must be checked after all other delimiters)
        if char1 == '\n':
            self.stream.next_char()
            # The raw value is '\n', but the PDA uses the TokenType
            return Token(tt.T_NEWLINE, '\n', start_line, start_column)

        # If it's not a delimiter, it's a CONTENT_CHUNK
        chunk_value = ""

        # Consume the first character of the chunk
        chunk_value += self.stream.next_char()

        # Loop to consume all subsequent characters until the start of ANY delimiter
        while True:
            char1 = self.stream.peek(1)
            char2 = self.stream.peek(2)

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
            chunk_value += self.stream.next_char()

        return Token(tt.T_CONTENT_CHUNK, chunk_value, start_line, start_column)


    def run(self):
        """ processes character stream into token list """
        while True:
            token = self._get_next_token()
            self.tokens.append(token)
            if token.ttype == tt.T_EOF:
                break
   
    def write_tokens_to_file(self, output_filename: str):
        """Writes tokens to output file."""
        are_we_good = True
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                for token in self.tokens:
                    f.write(token.to_ascii_line() + '\n')
        except Exception as e:
            are_we_good = False
            print(f"Error writing token output file: {e}")
    
        return are_we_good
        
    ## end of lexer class
    
    
if __name__ == '__main__':

    # if run in stand alone mode, set up to lex one file and save tokens in a .tok file
    # Usage: python Lexi.py <input_file>
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <input_file.sql>")
        sys.exit(1)

    input_filename = sys.argv[1]

    # Read entire input file content - our SQL source code
    try:
        with open(input_filename, 'r', encoding = 'utf-8') as f:
            source_code = f.read()        
        print("Lexi: SQL Source File Read")    
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    # Tokenize
    lexer = Lexer(source_code)
    lexer.run()
    
    print("Lexi: SQL Code Parsed")
    
    # Determine output filename (x.sql -> x.tok)
    base_name, ext = os.path.splitext(input_filename)
    output_filename = base_name + '.tok'

    # Write tokens to the output file
    result = lexer.write_tokens_to_file(output_filename)
    if result:
        print(f"Lexi: You can find the tokens in {output_filename}")
        sys.exit(0)
    else:
        sys.exit(1)
