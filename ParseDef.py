# This file contains definition of the SQL Statement Parser PDA, including all required constants.
import StructDef as tt  # so can pick up token type constants

# --- PDA State Definitions (Q) ---
Q_START = 'q_start'          # Ready for a new statement or context
Q_CODE = 'q_code'            # Inside a SQL code block (main context)
Q_BK_CMMT = 'q_bk_cmmt'      # Inside a block comment (/* ... */)
Q_LN_CMMT = 'q_ln_cmmt'      # Inside a line/dd comment (--)
Q_STR = 'q_str'              # Inside a single-quoted string ('...')
Q_ACCEPT = 'q_accept'        # Final state reached upon EOF (Accept)

# --- Stack Symbol Definitions (Γ) ---
G_Z0 = 'Z0'               # Initial stack bottom marker
G_CD = 'CC'               # Represents an ongoing SQL statement/code block (content chunk)
G_BC = 'BC'               # Context marker for a multi-line comment
G_LC = 'LC'               # Context marker for a single-line comment
G_STR = 'STR'               # Context marker for single-quoted string
G_POP = 'POP'         # Special symbol used in the action list to signify 'pop'

# --- Action Name Definitions (Translator Mode) ---
A_None = 'A_None'            # No execution action required
A_CopyBuffer = 'A_CopyBuffer'    # Copy token content to statement buffer
A_OutputCode = 'A_OutputCode'    # Finalize buffer, classify as CODE, and clear
A_OutputCmmt = 'A_OutputCmmt'    # Finalize buffer, classify as CMMT, and clear


# --- Transition Table (δ) ---
# Key: (Current_State, Input_Token_Type, Stack_Top)
# Value: (New_State, Stack_Action_List, Action_Name)
#
# Stack_Action_List: [] for NONE, [Symbol] for PUSH, [POP] for POP
# Note: The constants above need to be prefaced with pda. even though the
# following transitions are in this module because we will
# be importing them with this module aliased as pda.  Beware!

PDA_TRANSITIONS = {
    # --- STARTING NEW STATEMENTS (Z0 context) ---
    (Q_START, tt.CONTENT_CHUNK, G_Z0):      (Q_CODE, [G_CD], A_CopyBuffer),
    (Q_START, tt.START_BLOCK_COMMENT, G_Z0):(Q_BK_CMMT, [G_BC], A_None),
    (Q_START, tt.START_LINE_COMMENT, G_Z0): (Q_LN_CMMT, [G_LC], A_None),

    # --- CODE CONTEXT (= CC on stack) ---
    # Accumulate code
    (Q_CODE, 'CONTENT_CHUNK', G_CD):        (Q_CODE, [], A_CopyBuffer),

    # Begin nested comment contexts
    (Q_CODE, tt.START_BLOCK_COMMENT, G_CD): (Q_BK_CMMT, [G_BC], A_None),
    (Q_CODE, tt.START_LINE_COMMENT, G_CD):  (Q_LN_CMMT, [G_LC], A_None),

    # Begin string quote contexts
    (Q_CODE, tt.SINGLE_QUOTE, G_CD):        (Q_STR, [G_STR], A_CopyBuffer),

    # End statement (main goal)
    (Q_CODE, tt.END_STATEMENT, G_CD):       (Q_START, [G_POP], A_OutputCode),

    # EOF on code means final output
    (Q_CODE, tt.EOF, G_CD):                 (Q_ACCEPT, [G_POP], A_OutputCode),

    # --- MULTI-LINE COMMENT CONTEXT (G_BC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (Q_BK_CMMT, tt.CONTENT_CHUNK, G_BC):    (Q_BK_CMMT, [], A_CopyBuffer),

    # Ignore all other delimiters inside ML comment (e.g., Q_STR, START_BLOCK_COMMENT)
    (Q_BK_CMMT, tt.SINGLE_QUOTE, G_BC):     (Q_BK_CMMT, [], A_CopyBuffer),
    (Q_BK_CMMT, tt.START_LINE_COMMENT, G_BC):(Q_BK_CMMT, [], A_CopyBuffer),

    # End ML comment (pop the G_BC marker) -> Returns to previous context (S or Z0)
    (Q_BK_CMMT, tt.END_BLOCK_COMMENT, G_BC):(Q_CODE, [G_POP], A_OutputCmmt), # Return to S
    (Q_BK_CMMT, tt.END_BLOCK_COMMENT, G_Z0):  (Q_START, [G_POP], A_OutputCmmt), # Return to Z0

    # --- SINGLE-LINE COMMENT CONTEXT (G_LC on stack) ---
    # Accumulate comment content (non-ending chunk)
    (Q_LN_CMMT, tt.CONTENT_CHUNK, G_LC):    (Q_LN_CMMT, [], A_CopyBuffer),

    # Ignore everything until NEWLINE
    (Q_LN_CMMT, tt.SINGLE_QUOTE, G_LC):     (Q_LN_CMMT, [], A_CopyBuffer),

    # End SL comment -> Returns to previous context (S or Z0)
    (Q_LN_CMMT, tt.NEWLINE, G_LC):          (Q_CODE, [G_POP], A_OutputCmmt), # Return to S
    (Q_LN_CMMT, tt.NEWLINE, G_Z0):          (Q_START, [G_POP], A_OutputCmmt), # Return to Z0

        # --- SINGLE-QUOTED STRING CONTEXT (STR_S on stack) ---
    # Accumulate content inside the string (NOTE: no action on stack)
    (Q_STR, tt.CONTENT_CHUNK, G_STR):       (Q_STR, [], A_CopyBuffer),

    # Ignore delimiters inside the string
    (Q_STR, tt.START_BLOCK_COMMENT, G_STR): (Q_STR, [], A_CopyBuffer),

    # End string (pop G_STR marker) -> Returns to Q_CODE context
    (Q_STR, tt.SINGLE_QUOTE, G_STR):        (Q_CODE, [G_POP], A_CopyBuffer),

    # --- GLOBAL ACCEPT/REJECT ---
    (Q_START, tt.EOF, G_Z0):                (Q_ACCEPT, [], A_None),
}
