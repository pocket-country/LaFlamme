# Pedro.py - Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union
from StructDef import TokenType, Token, CharacterStream
import ParseDef as pda
import os

# --- PDA Definition ---

# The PDA's transitions as a dictionary:
# Key: (current_state, input_token_type, top_of_stack)
# Value: (next_state, stack_action: List[StackSymbol], action)
# !!!! Confirm this   - Empty list [] means POP the current top symbol.
#   - List with symbols means POP the current top, then PUSH the symbols in order.
#   - List with the current top symbol (e.g., [S]) means NO-OP (we pop and then push the same thing)/Consume.
# transition dictionary PDA_TRANSITIONS imported from ParseDev

# --- PDA Class Implementation ---

class PDA:
    def __init__(self, transitions: Dict):
        self.transitions = transitions
        self.stack: List[0] = [pda.Z0]  # Initialize with stack bottom Z0
        self.state: PDAState = pda.Q_START
        self.token_list: List[Token] = []

    def set_token_list(self, tokens: List[Token]):
        self.token_list = tokens
        
    def run(self) -> bool:
        self.state = pda.Q_START  # Reset state
        self.stack = [pda.Z0]  # Reset stack
        
        for token in self.token_list:
            current_top = self.stack[-1]
            transition_key = (self.state, token.type, current_top)
            
            # --- Check for Transition Rule ---
            if transition_key in self.transitions:
                next_state, stack_action, action = self.transitions[transition_key]
                self.state = next_state
                
                # --- Apply Stack Action ---
                # !!! confirm that we always pop stack.  Thought we matched top symbol, but this logic may be equivalent
                if stack_action:
                    # Pop the current top symbol  
                    self.stack.pop()
                    
                    # Push the new symbols (if any)
                    # Note: We push them onto the stack in reverse order of the list
                    # to maintain LIFO behavior for sequences.
                    for symbol in reversed(stack_action):
                        self.stack.append(symbol)
                
                # Debug print for tracing (remove this later)
                print(f"Token: {token.type.name:<20} | State: {next_state.name:<10} | Stack: {[s.name for s in self.stack]}")
                
            else:
                # --- Error State ---
                print("\n--- PARSING ERROR ---")
                print(f"REJECTED: No transition defined for:")
                print(f"  State: {self.state}")
                print(f"  Token: {token.type.name}")
                print(f"  Stack Top: {current_top}")
                print(f"  At: Line {token.line}, Col {token.column}")
                return False

        # --- Final Acceptance Check ---
        # Must end in an ACCEPT state with a clean stack (only Z0 remains)
        if self.state == pda.S_ACCEPT and len(self.stack) == 1 and self.stack[0] == pda.Z0:
            print("\n--- PARSING SUCCESS ---")
            return True
        else:
            print("\n--- PARSING FAILURE (Final Check) ---")
            print(f"Final State: {self.state}, Final Stack: {[s for s in self.stack]}")
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
            if token.type == TokenType.EOF:
                break
        
        # Parsing Phase
        parser = PDA(pda.PDA_TRANSITIONS)
        parser.set_token_list(tokens)
        
        print(f"Starting PDA run on {input_filename}...")
        is_accepted = parser.run()
        
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