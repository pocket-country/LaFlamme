# Pedro.py - The Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union
from StructDef import TokenType, Token, PDAState, StackSymbol, CharacterStream
import os

# --- PDA Definition ---

# Define the PDA's transitions as a dictionary:
# Key: (current_state, input_token_type, top_of_stack)
# Value: (next_state, stack_action: List[StackSymbol])
#   - Empty list [] means POP the current top symbol.
#   - List with symbols means POP the current top, then PUSH the symbols in order.
#   - List with the current top symbol (e.g., [S]) means NO-OP (we pop and then push the same thing)/Consume.

PDA_TRANSITIONS: Dict[Tuple[PDAState, TokenType, StackSymbol], Tuple[PDAState, List[StackSymbol]]] = {

    # -------------------------------------------------------------------------
    # INITIALIZATION and TERMINATION RULES
    # -------------------------------------------------------------------------

    # Start: Consume the first CODE_TEXT block and enter the main CODE state.
    (PDAState.S_START, TokenType.CONTENT_CHUNK, StackSymbol.Z0): 
        (PDAState.S_IN_CODE, [StackSymbol.Z0]), # No stack change, just transition state

    # Accept the statement end and return to START to look for the next statement.
    (PDAState.S_IN_CODE, TokenType.END_STATEMENT, StackSymbol.Z0):
        (PDAState.S_START, [StackSymbol.Z0]),

    # Accept EOF only when we are outside any open structure (Code state, empty stack)
    (PDAState.S_IN_CODE, TokenType.EOF, StackSymbol.Z0):
        (PDAState.S_ACCEPT, [StackSymbol.Z0]),
        
    # -------------------------------------------------------------------------
    # MAIN CODE CHUNK HANDLING (S_IN_CODE)
    # -------------------------------------------------------------------------
    
    # In code, consuming general content chunks (SQL code, whitespace)
    (PDAState.S_IN_CODE, TokenType.CONTENT_CHUNK, StackSymbol.Z0):
        (PDAState.S_IN_CODE, [StackSymbol.Z0]),

    # -------------------------------------------------------------------------
    # STRING MASKING RULES (Handles '...' escaping all delimiters)
    # -------------------------------------------------------------------------

    # Entering String Mode (from any state where a string starts)
    (PDAState.S_IN_CODE, TokenType.SINGLE_QUOTE, StackSymbol.Z0):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING, StackSymbol.Z0]), # Push String Marker
    
    # Content inside a string is consumed without affecting state/stack
    (PDAState.S_IN_STRING, TokenType.CONTENT_CHUNK, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),

    # String mode is immune to all other delimiters; they are treated as content.
    (PDAState.S_IN_STRING, TokenType.START_BLOCK_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.END_BLOCK_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.START_LINE_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.NEWLINE, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.END_STATEMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),

    # Exiting String Mode (POP the String Marker)
    (PDAState.S_IN_STRING, TokenType.SINGLE_QUOTE, StackSymbol.M_STRING):
        (PDAState.S_IN_CODE, []), # Pop M_STRING, return to IN_CODE
        
    # -------------------------------------------------------------------------
    # BLOCK COMMENT NESTING RULES (/* ... */)
    # -------------------------------------------------------------------------

    # Entry to block comment (from Code state)
    (PDAState.S_IN_CODE, TokenType.START_BLOCK_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C, StackSymbol.Z0]), # Push Block Marker

    # Content inside comment (ignore content, ignore line/statement ends)
    (PDAState.S_IN_BLOCK_C, TokenType.CONTENT_CHUNK, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),
    (PDAState.S_IN_BLOCK_C, TokenType.NEWLINE, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),
    (PDAState.S_IN_BLOCK_C, TokenType.END_STATEMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),

    # Nested Block Comment Entry (PUSH another marker)
    (PDAState.S_IN_BLOCK_C, TokenType.START_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C, StackSymbol.M_BLOCK_C]), # Replace M_BLOCK_C with [M_BLOCK_C, M_BLOCK_C]

    # Block Comment Exit (POP one marker)
    (PDAState.S_IN_BLOCK_C, TokenType.END_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, []), # Pop M_BLOCK_C

    # Final Block Comment Exit (POP the last marker, return to Code)
    (PDAState.S_IN_BLOCK_C, TokenType.END_BLOCK_COMMENT, StackSymbol.Z0): # Error case, should not happen if stack used correctly
        (PDAState.S_IN_CODE, [StackSymbol.Z0]),
        
    # -------------------------------------------------------------------------
    # LINE COMMENT RULES (-- to \n)
    # -------------------------------------------------------------------------

    # Entry to line comment (from Code state)
    (PDAState.S_IN_CODE, TokenType.START_LINE_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C, StackSymbol.Z0]), # Push Line Marker
        
    # Content inside line comment (ignore content)
    (PDAState.S_IN_LINE_C, TokenType.CONTENT_CHUNK, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
        
    # Line comments ignore all other delimiters except NEWLINE
    (PDAState.S_IN_LINE_C, TokenType.START_BLOCK_COMMENT, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
    (PDAState.S_IN_LINE_C, TokenType.END_BLOCK_COMMENT, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
    (PDAState.S_IN_LINE_C, TokenType.SINGLE_QUOTE, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
        
    # Line Comment Exit (POP the line marker, return to Code)
    (PDAState.S_IN_LINE_C, TokenType.NEWLINE, StackSymbol.M_LINE_C):
        (PDAState.S_IN_CODE, []), # Pop M_LINE_C

    # -------------------------------------------------------------------------
    # ERROR HANDLING (Any transition not defined above is an implicit error)
    # -------------------------------------------------------------------------

    # (Add explicit error state rules here later)
}

# --- PDA Class Implementation ---

class PDA:
    def __init__(self, transitions: Dict):
        self.transitions = transitions
        self.stack: List[StackSymbol] = [StackSymbol.Z0]  # Initialize with stack bottom Z0
        self.state: PDAState = PDAState.S_START
        self.token_list: List[Token] = []

    def set_token_list(self, tokens: List[Token]):
        self.token_list = tokens
        
    def run(self) -> bool:
        self.state = PDAState.S_START  # Reset state
        self.stack = [StackSymbol.Z0]  # Reset stack
        
        for token in self.token_list:
            current_top = self.stack[-1]
            transition_key = (self.state, token.token_type, current_top)
            
            # --- Check for Transition Rule ---
            if transition_key in self.transitions:
                next_state, stack_action = self.transitions[transition_key]
                self.state = next_state
                
                # --- Apply Stack Action ---
                if stack_action:
                    # Pop the current top symbol
                    self.stack.pop()
                    
                    # Push the new symbols (if any)
                    # Note: We push them onto the stack in reverse order of the list
                    # to maintain LIFO behavior for sequences.
                    for symbol in reversed(stack_action):
                        self.stack.append(symbol)
                
                # Debug print for tracing (remove this later)
                print(f"Token: {token.token_type.name:<20} | State: {next_state.name:<10} | Stack: {[s.name for s in self.stack]}")
                
            else:
                # --- Error State ---
                print("\n--- PARSING ERROR ---")
                print(f"REJECTED: No transition defined for:")
                print(f"  State: {self.state.name}")
                print(f"  Token: {token.token_type.name}")
                print(f"  Stack Top: {current_top.name}")
                print(f"  At: Line {token.line}, Col {token.column}")
                return False

        # --- Final Acceptance Check ---
        # Must end in an ACCEPT state with a clean stack (only Z0 remains)
        if self.state == PDAState.S_ACCEPT and len(self.stack) == 1 and self.stack[0] == StackSymbol.Z0:
            print("\n--- PARSING SUCCESS ---")
            return True
        else:
            print("\n--- PARSING FAILURE (Final Check) ---")
            print(f"Final State: {self.state.name}, Final Stack: {[s.name for s in self.stack]}")
            return False


# --- Main Execution Block ---

def parse_file(input_filename: str):
    """Tokenizes and then parses the input file."""
    
    # 1. Lexing Phase
    try:
        from Lexi import get_next_token # Import the lexer function
        
        # Read file content
        with open(input_filename, 'r') as f:
            source_code = f.read()

        stream = CharacterStream(source_code)
        tokens: List[Token] = []
        while True:
            token = get_next_token(stream)
            tokens.append(token)
            if token.token_type == TokenType.EOF:
                break
        
        # 2. Parsing Phase (The PDA)
        pda = PDA(PDA_TRANSITIONS)
        pda.set_token_list(tokens)
        
        print(f"Starting PDA run on {input_filename}...")
        is_accepted = pda.run()
        
        return is_accepted

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filename}")
        return False
    except ImportError:
        print("Error: Could not import Lexi. Please ensure 'Lexi.py' is in the same directory.")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python Pedro.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]
        
        if parse_file(input_filename):
            print(f"File {input_filename} processed successfully.")
        else:
            print(f"File {input_filename} contained a syntax error.")