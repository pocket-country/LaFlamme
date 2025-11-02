# Pedro.py - Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union

from StructDef import Token, CharacterStream
import StructDef as tt

import ParseDef as pda
import os

from Constants import TestStatus


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
    # note update to action being a single symbol/special symbol, rather than a list
    # note special action symbols and that we never push the bottom-o-stack marker
    def _handle_stack(self, action):
        match action:

            case pda.G_NUL:
            # if nothing to do ... empty list ... just exit
                return

            # if action is POP just pop.
            case pda.G_POP:
                # guard against malformed stack process, could test symbol or for []
                if len(self.stack) <= 1:
                    Print("ERROR: Attempted to pop initial stack symbol Z0")
                    return

                self.stack.pop()

            # OK here we have a symbol to push
            # Note that in a more powerful parser we would want to have a mechanism for
            # pushing a sequence of symbols but here there should only ever be one.
            # using python magic syntax to assert one symbol in list, and assign that symbol
            case G_CC | G_BC | G_LC | G_STR :
                self.stack.append(symbol_to_push)
                return

            # if we are here something bad happened.  I feel a disturbance in the force
            case _:
                print(f"CRITICAL ERROR: Unhandled or malformed stack action list: {stack_action_list}")
                # or we could put on big boy pants and raise an exception, halt

    def run(self, mode = 'verbose') -> bool:
        self.state = pda.Q_START  # Reset state
        self.stack = [pda.G_Z0]  # Reset stack


!!! this has to change to use our new token stream class
        for token in self.token_list:
            current_top = self.stack[-1]
            transition_trigger = (self.state, token.ttype, current_top)

            # --- Check for Transition Rule ---
            # if we find a rule ...
            if transition_trigger in self.transitions:
                transition_response = self.transitions[transition_trigger]
                
                # quick - log the transition!
                # !!!! what about that normailize thing around function name?
                xxx.trace.record_transition(
                    transition_key,
                    transition_response,
                    success = True
                )
                
                # now break it down into components and get 'er done
                next_state, stack_action, action = transition_response
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
                
                # log failed transition so capture trigger that failed
                FAIL_ACTION = 
                
                self.trace.record_transition(
                    trigger_key = trigger_key, 
                    action_value = ('NULL', 'NULL', 'NULL')
                    success = False
                )
                
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



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python Pedro.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]

        if parse_file(input_filename):
            print(f"File {input_filename} processed successfully.")
            sys.exit(0)
        else:
            print(f"File {input_filename} contained a syntax error.")
            sys.exit(1)
            