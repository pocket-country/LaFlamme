# This file contains definition of the SQL Statement Parser Pushdown Finite State Automaton (PDA)
# We have the token symbols, the state definitions, and the stacks symbols
# In addtion, because this is a "translator" we have a set of actions.
# 
# These are used to build a set of transition rules which drive the machine.
#
# Because these symbol sets (using constants to define symbols) define the PDA behavior, we 
# save this to save a machine "definition" or version, and hash it to provide an ID for that machine 
# in the instrumentation code.
#
# NOTE: TO YOU Mr. Itchy Fingers:  Editing comments will CHANGE hash even if functionality does not change - so
# Relax, Don't Do It When You Wanna Go To It, Relax, Don't Do It When You Wanna ...
#
#
# The prefered nomenclature, Dude: The PDA "Machine" is defined in terms of
# M = (Q,Sigma, Gamma, delta ,q_0, Z_0 ,F))
# Where 
#  Q: A finite set of states.
#  Sigma: A finite set of input symbols (the input alphabet).
#  Gamma: A finite set of stack symbols (the stack alphabet).
#  delta: The transition function, which defines the PDA's behavior.
#  q_0in Q: The start state.
#  Z_0 in Gamma: The initial stack symbol (placed on the stack at the beginning).
#  F subsete Q: A set of final or accepting states
#
# # --- Token Definitions --- (Sigma) --- 
# Delimiters
T_SINGLE_QUOTE = "'"
T_END_STATEMENT = ";"
T_START_BLOCK_COMMENT = "/*"
T_END_BLOCK_COMMENT = "*/"
T_START_LINE_COMMENT = "--"
# Content and Control
T_NEWLINE = "\\n"
T_CONTENT_CHUNK = "CONTENT_CHUNK"
T_EOF = "EOF"

# --- PDA State Definitions --- (Q) ---
Q_START = 'q_start'          # Ready for a new statement or context
Q_CODE = 'q_code'            # Inside a SQL code block (main context)
Q_BK_CMMT = 'q_bk_cmmt'      # Inside a block comment (/* ... */)
Q_LN_CMMT = 'q_ln_cmmt'      # Inside a line/dd comment (--)
Q_STR = 'q_str'              # Inside a single-quoted string ('...')
Q_ACCEPT = 'q_accept'        # Final state reached upon EOF (Accept)

# --- Stack Symbol Definitions --- (Γ)(Gamma) ---
G_Z0 = 'Z0'               # Initial stack bottom marker
G_CC = 'CC'               # Represents an ongoing content chunk - either a SQL statement/code block or comment text
G_BC = 'BC'               # Context marker for a multi-line comment
G_LC = 'LC'               # Context marker for a single-line comment
G_ST = 'ST'             # Context marker for single-quoted string
G_POP = 'POP'             # Special symbol used in the action list to signify 'pop'
G_NUL = 'NUL'             # Special symbol used in the action list to signify 'no action'

# --- Action Name Definitions (Translator Mode) ---
A_None = 'A_None'            # No execution action required
A_CopyBuffer = 'A_CopyBuffer'    # Copy token content to statement buffer
A_OutputCode = 'A_OutputCode'    # Finalize buffer, classify as CODE, and clear
A_OutputCmmt = 'A_OutputCmmt'    # Finalize buffer, classify as CMMT, and clear


# --- Transition Table --- (δ)(delta) ---
# The general form of the transition function is:
# delta :(Q X Sigma Union epsilon X  Gamma Union epsilon) ->  P(Q X Gagmma) Where 
#  (Q X Sigma X Gamma Union epsilon) is input representing: 
#  Current state, the input symbol (Token) being read and the symbol currently on the top of the stack (or epsilon if the stack is ignored or empty).
#
#  P(Q X Gamma)) defines the transition, a finite set containing pairs of the form q prime,gamma prime), where:
#   - q' in Q) is the next state, and 
#   - gamma' in Gamma the stack symbol the top of the stack 
#
# Note: restricting to a simple one-for-one stack symbol restricts the class of languages we can parse.  Were it a list we could do more
# but we don't need to here
#
# Note:  We add an 'action' function to the transition rule to manipulate the translator output as this is not just an acceptor.
# 
# This is implementd as a dictionary:
# Key: (Current_State, Input_Token_Type, Stack_Top)
# Value: (New_State, Stack_Action, Action_Name)
# Where Stack_Action: Symbol in Q_XXX for PUSH, G_POP for pop stack, G_NONE for no action

--- 
PDA_TRANSITIONS = {
    # --- STARTING NEW STATEMENTS (Z0 context) ---
    (Q_START, T_CONTENT_CHUNK, G_Z0):      (Q_CODE, G_CC, A_CopyBuffer),
    (Q_START, T_START_BLOCK_COMMENT, G_Z0):(Q_BK_CMMT, G_BC, A_None),
    (Q_START, T_START_LINE_COMMENT, G_Z0): (Q_LN_CMMT, G_LC, A_None),
    # slightly pathalogical but legal null program
    (Q_START, T_END_STATEMENT, G_Z0):      (Q_START, G_NUL , A_None),
    # nothing on stack, in start, hit a newline (so consumed), go to next line and see wazzup
    (Q_START, T_NEWLINE, G_Z0):            (Q_START, G_NUL, A_None),
   # in start, hit a newline as above, but there was a content chunk on the stack !!! confirm must be code?
    (Q_START, T_NEWLINE, G_CC):            (Q_CODE, G_NUL, A_None),
        
    # --- CODE CONTEXT (G_CC = CC on stack) ---
    # Accumulate code ... why would this happen?  Two contiguous code chunks equlvalent to one code chunk ...
    (Q_CODE, T_CONTENT_CHUNK, G_CC):        (Q_CODE, G_NUL, A_CopyBuffer),
    # skip a newline, stay in code (as no ";" yet) and keep accumulating ..
    (Q_CODE, T_NEWLINE, G_CC):              (Q_CODE, G_NUL, A_None),

    # Begin nested comment contexts
    (Q_CODE, T_START_BLOCK_COMMENT, G_CC):  (Q_BK_CMMT, G_BC, A_None),
    (Q_CODE, T_START_LINE_COMMENT, G_CC):   (Q_LN_CMMT, G_LC, A_None),

    # Begin string quote contexts
    (Q_CODE, T_SINGLE_QUOTE, G_CC):         (Q_STR, G_ST, A_CopyBuffer),

    # End statement (main goal)
    (Q_CODE, T_END_STATEMENT, G_CC):        (Q_START, G_POP, A_OutputCode),

    # EOF on code means final output - but maybe should have a ";"?
    (Q_CODE, T_EOF, G_CC):                  (Q_ACCEPT, G_POP, A_OutputCode),

    # --- Block/ML Comment Context (G_BC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (Q_BK_CMMT, T_CONTENT_CHUNK, G_BC):     (Q_BK_CMMT, G_NUL, A_CopyBuffer),

    # Ignore all other delimiters inside Block comment (e.g., Q_STR, START_BLOCK_COMMENT)
    (Q_BK_CMMT, T_SINGLE_QUOTE, G_BC):      (Q_BK_CMMT, G_NUL, A_CopyBuffer),
    (Q_BK_CMMT, T_START_LINE_COMMENT, G_BC):(Q_BK_CMMT, G_NUL, A_CopyBuffer),

    # End Block comment (pop the G_BC marker) -> Returns to previous context 
    # ... which was a comment (!!!confirm)
    (Q_BK_CMMT, T_END_BLOCK_COMMENT, G_BC): (Q_START, G_POP, A_OutputCmmt), 
    # ... which was a code line ... (!!! confirm)
    (Q_BK_CMMT, T_END_BLOCK_COMMENT, G_CC): (Q_CODE, G_POP, A_OutputCmmt), 
    # ... which was the bottom of the stack (!!!) confirm
    (Q_BK_CMMT, T_END_BLOCK_COMMENT, G_Z0): (Q_START, G_POP, A_OutputCmmt),

    # --- SINGLE-LINE COMMENT CONTEXT (G_LC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (Q_LN_CMMT, T_CONTENT_CHUNK, G_LC):     (Q_LN_CMMT, G_NUL, A_CopyBuffer),

    # Ignore everything until NEWLINE
    (Q_LN_CMMT, T_SINGLE_QUOTE, G_LC):      (Q_LN_CMMT, G_NUL, A_CopyBuffer),

    # End SL comment -> Returns to previous context (S or Z0)
    (Q_LN_CMMT, T_NEWLINE, G_LC):           (Q_CODE, G_POP, A_OutputCmmt), # Return to S
    (Q_LN_CMMT, T_NEWLINE, G_Z0):           (Q_START, G_POP, A_OutputCmmt), # Return to Z0

        # --- SINGLE-QUOTED STRING CONTEXT (STR_S on stack) ---
    # Accumulate content inside the string (NOTE: no action on stack)
    (Q_STR, T_CONTENT_CHUNK, G_ST):        (Q_STR, G_NUL, A_CopyBuffer),

    # Ignore delimiters inside the string
    (Q_STR, T_START_BLOCK_COMMENT, G_ST):  (Q_STR, G_NUL, A_CopyBuffer),

    # End string (pop G_ST marker) -> Returns to Q_CODE context
    (Q_STR, T_SINGLE_QUOTE, G_ST):         (Q_CODE, G_POP, A_CopyBuffer),

    # --- GLOBAL ACCEPT/REJECT ---
    (Q_START, T_EOF, G_Z0):                 (Q_ACCEPT, G_NUL, A_None),
}
