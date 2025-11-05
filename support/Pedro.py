# --- Pedro.py --- Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union
import os

from .StructDef import Token, CharacterStream
from . import ParseDef as pda

# --- PDA Class Implementation ---
class PDA:
    def __init__(self, transitions: Dict, tokens, trans_trace):
        self.transitions = transitions
        self.stack: List[0] = [pda.G_Z0]  # Initialize with stack bottom Z0
        self.state: PDAState = pda.Q_START
        self.token_list: List[Token] = tokens
        self.datalog = trans_trace          # we assume this has been properly initialized

    def _handle_stack(self, action):
        """ 
        private method. Only side effects - stack manipulation.
        Note special action symbols and that we never push the bottom-o-stack marker
        Note: Only one stach symbol at a time
        """
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
            case pda.G_CC | pda.G_BC | pda.G_LC | pda.G_ST as symbol_to_push:
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
            transition_trigger = (self.state, token.ttype, current_top)

            # --- Check for Transition Rule ---
            # if we find a rule ...
            if transition_trigger in self.transitions:
                transition_response = self.transitions[transition_trigger]
                
                # quick - log the transition!
                self.datalog.record_transition(
                    transition_trigger,
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
                failed_transaction_response = ('NULL', 'NULL', 'NULL')
                self.datalog.record_transition(
                    transition_trigger, 
                    failed_transaction_response,
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
    
    # end of PDA class definition
    
class LesserTransTrace:
    
    def __init__(self):           
        # because the AI loves me more wiht this here ...
        pass            

    def _normalize_action_value(self, action_tuple):
        """Replaces function references in the action tuple with stable strings."""
        # Assuming action_tuple = (<next_state>, <stack_action>, <execution_action>)
        # The execution_action (index 2) is the function reference.
        
        # Get the function's name string:
        func_name = action_tuple[2].__name__ if callable(action_tuple[2]) else str(action_tuple[2])
        
        # Return the new tuple with the name instead of the reference
        return action_tuple[0], action_tuple[1], func_name       
        
    def record_transition(self, trigger_key, action_value, success = True):
        """prints a single transition (real or ghost) console."""
        # Ensure trigger_key is represented as a string for storage
        trigger_str = str(trigger_key) 
        
        if success:
            status = "Next"
            normalized_action = self._normalize_action_value(action_value)
        else:
            status = "Fail"
            normalized_action = action_value
            
        print(f"trigger: {trigger_str}, action: {normalized_action}, result: {status}")

if __name__ == '__main__':
    
    from .StructDef import CharacterStream
    from . import Lexi
    
    # Run in stand-alone mode just to test, with dummy tracer (hey! Dependency Injection, I'm now a Kool Kid)
    # Because this is the PDA/Parser, we do have to run lexi first and do a bit of processing
    # ... so basically repeat Lexi Main code and then test PDA functionality
    # For real runs i.e "the application" all this stuff is handled Parse.py
    
    if len(sys.argv) < 2:
        print("Usage: python Pedro.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]

    # Lexing Phase
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
    lexer = Lexi.Lexer(source_code)
    lexer.run()
    
    print("Lexi (via Pedro): SQL Code Parsed")
    
    # Determine output filename (x.sql -> x.tok)
    base_name, ext = os.path.splitext(input_filename)
    output_filename = base_name + '.tok'

    # Write tokens to the output file
    result = lexer.write_tokens_to_file(output_filename)
    if result:
        print(f"Lexi (via Pedro): You can find the tokens in {output_filename}")
    else:
        sys.exit(1)

    # set up ruidimentary logger
    logger = LesserTransTrace()
    
    # instantiate and call our PDA to parser
    parser = PDA(pda.PDA_TRANSITIONS, lexer.tokens, logger)
    result = parser.run()
    if result:
        print(f"Pedro: File parsed correctly")
        sys.exit(0)
    else:
        sys.exit(1)
