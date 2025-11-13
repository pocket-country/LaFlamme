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

# --- Stack Symbol Definitions --- (Γ)(Gamma) ---
G_Z0 = 'Z0'               # Initial stack bottom marker
G_CC = 'CC'               # Represents an ongoing content chunk - either a SQL statement/code block or comment text
G_BC = 'BC'               # Context marker for a multi-line comment
G_LC = 'LC'               # Context marker for a single-line comment
G_ST = 'ST'               # Context marker for single-quoted string
G_POP = 'POP'             # Special symbol used in the action list to signify 'pop'
G_NUL = 'NUL'             # Special symbol used in the action list to signify 'no action'

# --- Action Name Definitions (Translator Mode) ---
A_None = 'A_None'            # No execution action required
A_Content2Buffer = 'Content2Buffer'    # Copy token content to statement buffer
# these now happen automatically on pop
#A_OutputCode = 'A_OutputCode'    # Finalize buffer, classify as CODE, and clear
#A_OutputCmmt = 'A_OutputCmmt'    # Finalize buffer, classify as CMMT, and clear


# --- Transition Table --- (δ)(delta) ---
# The general form of the transition function is:
# delta :(Q X Sigma Union epsilon X  Gamma Union epsilon) ->  P(Q X Gamma) Where 
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
# Key: (Input_Token_Type, Current_State, Stack_Top)
# Value: (New_State, Stack_Action, Action_Name)
# Where Stack_Action: Symbol in Q_XXX for PUSH, G_POP for pop stack, G_NONE for no action


PDA_TRANSITIONS = {
    # --- STARTING NEW STATEMENTS (Z0 context) ---
    (T_CONTENT_CHUNK, Q_START, G_Z0):      (Q_CODE, G_CC, A_CopyBuffer),
    (T_START_BLOCK_COMMENT, Q_START, G_Z0):(Q_BK_CMMT, G_BC, A_None),
    (T_START_LINE_COMMENT, Q_START, G_Z0): (Q_LN_CMMT, G_LC, A_None),
    # slightly pathalogical but legal null program
    (T_END_STATEMENT, Q_START, G_Z0):      (Q_START, G_NUL , A_None),
    # nothing on stack, in start, hit a newline (so consumed), go to next line and see wazzup
    (T_NEWLINE, Q_START, G_Z0):            (Q_START, G_NUL, A_None),
    # in start, hit a newline as above, but there was a content chunk on the stack !!! confirm must be code?
    (T_NEWLINE, Q_START, G_CC):            (Q_CODE, G_NUL, A_None),
        
    # --- CODE CONTEXT (G_CC = CC on stack) ---
    # Accumulate code ... why would this happen?  Two contiguous code chunks equlvalent to one code chunk ...
    (T_CONTENT_CHUNK, Q_CODE, G_CC):        (Q_CODE, G_NUL, A_CopyBuffer),
    # skip a newline, stay in code (as no ";" yet) and keep accumulating ..
    (T_NEWLINE, Q_CODE, G_CC):              (Q_CODE, G_NUL, A_None),

    # Begin nested comment contexts
    (T_START_BLOCK_COMMENT, Q_CODE, G_CC):  (Q_BK_CMMT, G_BC, A_None),
    (T_START_LINE_COMMENT, Q_CODE, G_CC):   (Q_LN_CMMT, G_LC, A_None),

    # Begin string quote contexts
    (T_SINGLE_QUOTE, Q_CODE, G_CC):         (Q_STR, G_ST, A_CopyBuffer),

    # End statement (main goal)
    (T_END_STATEMENT, Q_CODE, G_CC):        (Q_START, G_POP, A_None),

     # --- Block/ML Comment Context (G_BC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (T_CONTENT_CHUNK, Q_BK_CMMT, G_BC):     (Q_BK_CMMT, G_NUL, A_CopyBuffer),

    # Ignore all other delimiters inside Block comment (e.g., Q_STR, START_BLOCK_COMMENT)
    (T_SINGLE_QUOTE, Q_BK_CMMT, G_BC):      (Q_BK_CMMT, G_NUL, A_CopyBuffer),
    (T_START_LINE_COMMENT, Q_BK_CMMT, G_BC):(Q_BK_CMMT, G_NUL, A_CopyBuffer),

    # End Block comment (pop the G_BC marker) -> Returns to previous context 
    # ... which was a comment (!!!confirm)
    (T_END_BLOCK_COMMENT, Q_BK_CMMT, G_BC): (Q_START, G_POP, A_None), 
    # ... which was a code line ... (!!! confirm)
    (T_END_BLOCK_COMMENT, Q_BK_CMMT, G_CC): (Q_CODE, G_POP, A_None), 
    # ... which was the bottom of the stack (!!!) confirm
    (T_END_BLOCK_COMMENT, Q_BK_CMMT, G_Z0): (Q_START, G_POP, A_None),

    # --- SINGLE-LINE COMMENT CONTEXT (G_LC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (T_CONTENT_CHUNK, Q_LN_CMMT, G_LC):     (Q_LN_CMMT, G_NUL, A_CopyBuffer),

    # Ignore everything until NEWLINE
    (T_SINGLE_QUOTE, Q_LN_CMMT, G_LC):      (Q_LN_CMMT, G_NUL, A_CopyBuffer),

    # End SL comment -> Returns to previous context (S or Z0)
    (T_NEWLINE, Q_LN_CMMT, G_LC):           (Q_CODE, G_POP, A_None),  # Return to S
    (T_NEWLINE, Q_LN_CMMT, G_Z0):           (Q_START, G_POP, A_None), # Return to Z0
 
    # --- SINGLE-QUOTED STRING CONTEXT (STR_S on stack) ---
    # Accumulate content inside the string (NOTE: no action on stack)
    (T_CONTENT_CHUNK, Q_STR, G_ST):        (Q_STR, G_NUL, A_CopyBuffer),

    # Ignore delimiters inside the string
    (T_START_BLOCK_COMMENT, Q_STR, G_ST):  (Q_STR, G_NUL, A_CopyBuffer),

    # End string (pop G_ST marker) -> Returns to Q_CODE context
    (T_SINGLE_QUOTE, Q_STR, G_ST):         (Q_CODE, G_POP, A_CopyBuffer)
}
