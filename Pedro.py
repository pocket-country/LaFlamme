# Pedro.py - Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union

from StructDef import Token, CharacterStream
import StructDef as tt

import ParseDef as pda
import os

# --- PDA Definition ---

# The PDA's transitions as a dictionary:
# Key: (current_state, input_token_type, top_of_stack)
# Value: (next_state, stack_action: List[StackSymbol], action)
# transition dictionary PDA_TRANSITIONS imported from ParseDev

# --- PDA Class Implementation ---

class PDA:
    def __init__(self, transitions: Dict):
        self.transitions = transitions
        self.stack: List[0] = [pda.G_Z0]  # Initialize with stack bottom Z0
        self.state: PDAState = pda.Q_START
        self.token_list: List[Token] = []

    def set_token_list(self, tokens: List[Token]):
        self.token_list = tokens

    # private method. Only side effects - stack manipulation.
    def _handle_stack(self, action_list):
        match action_list:

            case []:
            # if nothing to do ... empty list ... just exit
                return

            # if action is POP just pop.
            case [pda.G_POP]:
                # guard against malformed stack process, could test symbol or for []
                if len(self.stack) <=1:
                    Print("ERROR: Attempted to pop initial stack symbol Z0")
                    return

                self.stack.pop()

            # OK here we have a symbol to push
            # Note that in a more powerful parser we would want to have a mechanism for
            # pushing a sequence of symbols but here there should only ever be one.
            # using python magic syntax to assert one symbol in list, and assign that symbol
            case [symbol_to_push]:
                self.stack.append(symbol_to_push)
                return

            # if we are here something bad happened.  I feel a disturbance in the force
            case _:
                print(f"CRITICAL ERROR: Unhandled or malformed stack action list: {stack_action_list}")
                # or we could put on big boy pants and raise an exception, halt

    def run(self, mode = 'verbose') -> bool:
        self.state = pda.Q_START  # Reset state
        self.stack = [pda.G_Z0]  # Reset stack

        for token in self.token_list:
            current_top = self.stack[-1]
            transition_key = (self.state, token.ttype, current_top)

            # --- Check for Transition Rule ---
            # if we find a rule ...
            if transition_key in self.transitions:
                next_state, stack_action, action = self.transitions[transition_key]
                self.state = next_state

                # --- Apply Stack Action ---
                self._handle_stack(stack_action)

                # Debug print for tracing (remove this later)
                if mode == 'verbose':
                    print(f"Token: {token.ttype:<20} | State: {next_state:<10} | Stack: {[s for s in self.stack]}")

            else:
                # --- Error State ---
                if mode == 'verbose':
                    print("\n--- PARSING ERROR ---")
                    print(f"REJECTED: No transition defined for:")
                    print(f"  State: {self.state}")
                    print(f"  Token: {token.ttype}")
                    print(f"  Stack Top: {current_top}")
                    print(f"  At: Line {token.line}, Col {token.column}")
                return False

        # --- Final Acceptance Check ---
        # Must end in an ACCEPT state with a clean stack (only Z0 remains)
        if self.state == pda.Q_ACCEPT and len(self.stack) == 1 and self.stack[0] == pda.G_Z0:
            if mode == 'verbose':
                print("\n--- PARSING SUCCESS ---")
            return True
        else:
            if mode == verbose:
                print("\n--- PARSING FAILURE (Final Check) ---")
                print(f"Final State: {self.state}, Final Stack: {[s for s in self.stack]}")
            return False


# --- Main Execution Block ---

def parse_file(input_filename: str, mode = "quite"):
    """Tokenizes and then parses the input file."""

    # Lexing Phase
    try:
        from Lexi import get_next_token # Import the lexer function

        # Read file content
        with open(input_filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filename}")
        return False
    except ImportError:
        print("Error: Could not import Lexi. Please ensure 'Lexi.py' is in the same directory.")
        return False

    print(f"Running parser on {input_filename}\n")

    # Iterate, buidling a token list
    stream = CharacterStream(source_code)
    tokens: List[Token] = []
    while True:
        token = get_next_token(stream)
        tokens.append(token)
        if token.ttype == tt.EOF:
            break

    # for diagnostics, write token list to a file
    base_name, ext = os.path.splitext(input_filename)
    token_filename = base_name + '.tok'

    try:
        with open(token_filename, 'w', encoding='utf-8') as f:
            for token in tokens:
                f.write(token.to_test_line() + '\n')

    except Exception as e:
        print(f"Error in token output file: {e}")
        return False

    print(f"Lexi OK, tokens in {token_filename}\n")

    # Parsing Phase
    # instantiate parser class, load in tokens ... 
    parser = PDA(pda.PDA_TRANSITIONS)
    parser.set_token_list(tokens)

    # and run ...
    print(f"Starting PDA run ...")
    is_accepted = parser.run()

    return is_accepted


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python Pedro.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]

        if parse_file(input_filename):
            print(f"File {input_filename} processed successfully.")
        else:
            print(f"File {input_filename} contained a syntax error.")