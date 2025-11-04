# --- Pedro.py --- Pushdown Automaton (PDA) Parser
import sys
from typing import List, Tuple, Dict, Optional, Union
import os



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
        
        for token in self.token_list:
            current_top = self.stack[-1]
            transition_trigger = (self.state, token.ttype, current_top)

            # --- Check for Transition Rule ---
            # if we find a rule ...
            if transition_trigger in self.transitions:
                transition_response = self.transitions[transition_trigger]
                
                # quick - log the transition!
                # !!!! what about that normailize thing around function name?
                self.datalog.record_transition(
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
                
                self.datalog.record_transition(
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
    
    # end of PDA class definition
    
    class LesserTransTrace:
        
    def __init__:           
        # because the AI loves me more wiht this here ...
        pass            

    def _normalize_action_value(action_tuple):
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
            normalized_action = _normalize_action_value(action_value)
        else:
            status = "Fail"
            normalized_action = action_value
            
        print(f"trigger: {trigger_str}, action: {normalized_action}, result: {status}")

if __name__ == '__main__':
    
    # Run in stand-alone mode just to test, with dummy tracer (hey! Dependency Injection, I'm now a Kool Kid)
    # Because this is the PDA/Parser, we do have to run lexi first and do a bit of processing
    # For real runs all this stuff is handled Parse.py
    from .StructDef import Token, CharacterStream
    from . import lexi
    from . import ParseDef as parser_definition

    if len(sys.argv) < 2:
        print("Usage: python Pedro.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]

    # Lexing Phase
    try:
        from Lexi import get_next_token # Import the lexer function

        # Read file content
        with open(input_file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file_path}")
    except ImportError:
        print("Error: Could not import Lexi. Please ensure 'Lexi.py' is in the same directory.")

    if verbose: print(f"Running parser on {input_file_path}\n")

    # Iterate, buidling a token list from just read source code
    stream = CharacterStream(source_code)
    lexer = lexer(stream)
    lexer.run()
    
    print("Pedro: Source code read => tokens)
    
   # Determine output filename (x.sql -> x.tok)
    base_name, ext = os.path.splitext(input_filename)
    output_filename = base_name + '.tok'

    # Write tokens to the output file in case we want to inspect 'em
    result = lexer.write_tokens_to_file
    if result:
        print(f"Lexi: You can find the tokens in {output_filename}")

    # set up ruidimentary logger
    logger = LesserTransTrace()
    
    # instantiate and call our PDA to parser
    pda = PDA(def __init__(self, parser_definition, lexer.tokens, logger):
    
