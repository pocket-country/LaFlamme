from StrucDef import Token, TokenType
from enum import Enum
from typing import List, Tuple, Dict, Any
import sys
import os

# --- 1. PDA States ---
class PDAState(Enum):
    """Defines the non-terminal states of the Pushdown Automaton."""
    S_START = 'START'         # Initial state, expecting a new statement
    S_IN_CODE = 'IN_CODE'     # Inside a CodeStatement, expecting code or delimiters
    S_IN_STRING = 'IN_STRING' # Inside a string literal ('...'), masking everything
    S_IN_COMMENT = 'IN_COMMENT' # Inside a block comment (/* ... */)
    S_ERROR = 'ERROR'         # Reject state (should stop execution)
    S_ACCEPT = 'ACCEPT'       # Final state

# --- 2. Stack Symbols ---
class StackSymbol(Enum):
    """Defines the symbols used on the PDA stack for context tracking."""
    Z0 = '$'                  # Stack Bottom Marker
    M_STRING = 'M_STRING'     # String Masking Marker
    M_BLOCK_C = 'M_BLOCK_C'   # Block Comment Nesting Marker

# --- 3. Transition Type Definition ---
# Transition Key: (current_state, input_token_type, top_of_stack_symbol)
# Transition Value: (next_state, stack_action)
# Stack Action: List of symbols to replace the top of the stack (empty list means POP)

PDATransition = Tuple[PDAState, TokenType, StackSymbol]
PDAAction = Tuple[PDAState, List[StackSymbol]]

# --- 4. PDA Transition Table ---
PDA_TRANSITIONS: Dict[PDATransition, PDAAction] = {
    # =========================================================================
    # START STATE: Looking for the beginning of a Statement
    # =========================================================================

    # (S_START, CONTENT_CHUNK, Z0) -> Start of a Code Statement
    (PDAState.S_START, TokenType.CONTENT_CHUNK, StackSymbol.Z0): 
        (PDAState.S_IN_CODE, [StackSymbol.Z0]), # Stack stays: Z0
    
    # (S_START, START_BLOCK_COMMENT, Z0) -> Start of a top-level Comment Statement
    (PDAState.S_START, TokenType.START_BLOCK_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_COMMENT, [StackSymbol.M_BLOCK_C, StackSymbol.Z0]), # Push M_BLOCK_C

    # (S_START, EOF, Z0) -> Program finished correctly
    (PDAState.S_START, TokenType.EOF, StackSymbol.Z0): 
        (PDAState.S_ACCEPT, [StackSymbol.Z0]), # Stack stays: Z0

    # =========================================================================
    # IN_CODE STATE: Handling code chunks, delimiters, and entering nested scopes
    # =========================================================================

    # (S_IN_CODE, CONTENT_CHUNK, M) -> Continue consuming code chunks
    (PDAState.S_IN_CODE, TokenType.CONTENT_CHUNK, StackSymbol.Z0):
        (PDAState.S_IN_CODE, [StackSymbol.Z0]),
        
    # [ACTION: START STRING MASKING]
    # (S_IN_CODE, SINGLE_QUOTE, Z0) -> Enter string mode
    (PDAState.S_IN_CODE, TokenType.SINGLE_QUOTE, StackSymbol.Z0):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING, StackSymbol.Z0]), # Push M_STRING

    # [ACTION: START NESTED BLOCK COMMENT]
    # (S_IN_CODE, START_BLOCK_COMMENT, Z0) -> Enter comment mode from code
    (PDAState.S_IN_CODE, TokenType.START_BLOCK_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_COMMENT, [StackSymbol.M_BLOCK_C, StackSymbol.Z0]), # Push M_BLOCK_C

    # [ACTION: END STATEMENT]
    # (S_IN_CODE, END_STATEMENT, Z0) -> Statement finished, go to START state
    (PDAState.S_IN_CODE, TokenType.END_STATEMENT, StackSymbol.Z0):
        (PDAState.S_START, [StackSymbol.Z0]), # Statement boundary reached

    # =========================================================================
    # IN_STRING STATE: Masking all input until closing quote is found
    # =========================================================================

    # (S_IN_STRING, CONTENT_CHUNK, M_STRING) -> Consume all content (includes spaces/dashes)
    (PDAState.S_IN_STRING, TokenType.CONTENT_CHUNK, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
        
    # (S_IN_STRING, START_BLOCK_COMMENT, M_STRING) -> IGNORE delimiters inside string
    (PDAState.S_IN_STRING, TokenType.START_BLOCK_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),

    # (S_IN_STRING, END_STATEMENT, M_STRING) -> IGNORE delimiters inside string
    (PDAState.S_IN_STRING, TokenType.END_STATEMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
        
    # [ACTION: END STRING MASKING]
    # (S_IN_STRING, SINGLE_QUOTE, M_STRING) -> Found closing quote, pop M_STRING and return to IN_CODE
    (PDAState.S_IN_STRING, TokenType.SINGLE_QUOTE, StackSymbol.M_STRING):
        (PDAState.S_IN_CODE, []), # POP M_STRING
    
    # =========================================================================
    # IN_COMMENT STATE: Handling nested block comments
    # =========================================================================

    # (S_IN_COMMENT, CONTENT_CHUNK, M_BLOCK_C) -> Consume content inside comment
    (PDAState.S_IN_COMMENT, TokenType.CONTENT_CHUNK, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_COMMENT, [StackSymbol.M_BLOCK_C]),
        
    # (S_IN_COMMENT, START_BLOCK_COMMENT, M_BLOCK_C) -> **NESTING:** Push another M_BLOCK_C
    (PDAState.S_IN_COMMENT, TokenType.START_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_COMMENT, [StackSymbol.M_BLOCK_C, StackSymbol.M_BLOCK_C]), # Push M_BLOCK_C

    # [ACTION: POP NESTING LEVEL]
    # (S_IN_COMMENT, END_BLOCK_COMMENT, M_BLOCK_C) -> Pop one level of nesting
    (PDAState.S_IN_COMMENT, TokenType.END_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_CODE, []), # POP M_BLOCK_C. Transition back to IN_CODE (which may implicitly return to S_START next)
        
    # =========================================================================
    # ERROR CONDITIONS (Not exhaustive, but catches key missing end tags)
    # =========================================================================
    
    # (S_IN_STRING, EOF, M_STRING) -> Unterminated string literal
    (PDAState.S_IN_STRING, TokenType.EOF, StackSymbol.M_STRING):
        (PDAState.S_ERROR, [StackSymbol.Z0]), 
        
    # (S_IN_COMMENT, EOF, M_BLOCK_C) -> Unterminated block comment
    (PDAState.S_IN_COMMENT, TokenType.EOF, StackSymbol.M_BLOCK_C):
        (PDAState.S_ERROR, [StackSymbol.Z0]),
}

# -----------------------------------------------------------------------------
# CORE PDA EXECUTION CLASS
# -----------------------------------------------------------------------------

class PDA:
    def __init__(self, token_list: List[Token]):
        self.tokens = token_list
        self.token_index = 0
        self.stack: List[StackSymbol] = [StackSymbol.Z0]
        self.state = PDAState.S_START
        self.status_message = "Parsing in progress."
        
        # NOTE: The transition table is defined globally (PDA_TRANSITIONS)

    def get_current_token(self) -> Token:
        if self.token_index < len(self.tokens):
            return self.tokens[self.token_index]
        # Should not happen if EOF token is handled correctly, but safety first
        return Token(TokenType.EOF, "", 0, 0) 

    def advance_token(self):
        if self.token_index < len(self.tokens):
            self.token_index += 1

    def push(self, symbol: StackSymbol):
        self.stack.append(symbol)

    def pop(self) -> Optional[StackSymbol]:
        if len(self.stack) > 1: # Never pop the Z0 bottom marker unless accepting
            return self.stack.pop()
        return None

    def execute_transition(self, action: PDAAction):
        next_state, stack_action = action
        self.state = next_state
        
        # Stack Action Logic: POP, PUSH, or REPLACE
        if len(stack_action) == 0:
            # POP action (stack_action is [])
            self.pop()
        elif len(stack_action) == 1 and stack_action[0] == self.stack[-1]:
            # No change (e.g., [Z0] remains [Z0]). Do nothing.
            pass
        elif len(stack_action) == 2 and stack_action[1] == self.stack[-1]:
            # Simple PUSH action: [M_NEW, M_OLD] means push M_NEW
            self.push(stack_action[0])
        elif len(stack_action) > 0:
            # General Replace: Pop the top, then push the sequence (more complex, avoiding for now)
            # For simplicity, we are using the POP/PUSH approach defined above
            pass

    def parse(self) -> bool:
        """Runs the PDA until an ACCEPT or ERROR state is reached."""
        while self.state not in [PDAState.S_ACCEPT, PDAState.S_ERROR]:
            token = self.get_current_token()
            top_of_stack = self.stack[-1]
            
            # The key to the transition table lookup
            transition_key = (self.state, token.type, top_of_stack)
            
            if transition_key in PDA_TRANSITIONS:
                action = PDA_TRANSITIONS[transition_key]
                self.execute_transition(action)
                self.advance_token()
                
            # Line Comment logic (to be added later, needs lookahead logic from lexer)
            elif token.type == TokenType.START_LINE_COMMENT:
                self.status_message = f"Error: Line comments not yet implemented for parsing."
                self.state = PDAState.S_ERROR
                
            # Default Error Handling
            else:
                self.status_message = (
                    f"PARSE ERROR at {token.to_test_line()}: "
                    f"No valid transition from State={self.state.value}, "
                    f"Token={token.type.value}, Stack Top={top_of_stack.value}"
                )
                self.state = PDAState.S_ERROR
                
        # Final Report
        if self.state == PDAState.S_ACCEPT:
            self.status_message = "Parsing successful: Program accepted."
            return True
        else:
            print(self.status_message, file=sys.stderr)
            return False

# -----------------------------------------------------------------------------
# STANDALONE EXECUTION (Requires Lexi.py and StrucDef.py in the same directory)
# -----------------------------------------------------------------------------

def parse_file(input_filename: str) -> bool:
    """Tokenizes the file and then runs the PDA parser."""
    # NOTE: Requires Lexi.py and StrucDef.py to be present for tokenization.
    try:
        # Assuming tokenization logic is available (either imported or directly copied)
        from Lexi import tokenize_file # This is a placeholder for actual import
        token_list = tokenize_file(input_filename)
        
        # If tokenization fails (e.g., returns None or empty list)
        if not token_list or token_list[-1].type != TokenType.EOF:
             print(f"Error: Tokenization failed for {input_filename}")
             return False

        pda = PDA(token_list)
        return pda.parse()

    except ImportError:
        print("Error: Could not import tokenization logic from Lexi.py.")
        return False
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        return False

if __name__ == '__main__':
    # Usage: python Pedro.py <input_file.sql>
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <input_file.sql>")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    
    # We will need to use a working version of tokenize_file once we finalize Lexi.py
    # For now, this is a conceptual entry point
    print(f"Attempting to parse: {input_filename}")
    # parse_file(input_filename) # Uncomment once Lexi.py import is working
    # Placeholder for running tests
    print("PDA is defined. Next steps: fill in line comment logic and finalize Lexi.py integration.")
