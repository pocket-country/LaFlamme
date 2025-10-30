# This file contains definition of the SQL Statement Parser PDA, including all required constants.

# --- PDA State Definitions (Q) ---
Q_START = 'q_start'          # Ready for a new statement or context
Q_CODE = 'q_code'            # Inside a SQL code block (main context)
Q_CMMT_ML = 'q_cmmt_ml'      # Inside a multi-line comment (/* ... */)
Q_CMMT_SL = 'q_cmmt_sl'      # Inside a single-line comment (--)
Q_STR_S = 'q_str_s'          # Inside a single-quoted string ('...')
Q_STR_D = 'q_str_d'          # Inside a double-quoted string ("...")
Q_ACCEPT = 'q_accept'        # Final state reached upon EOF (Accept)

# --- Stack Symbol Definitions (Γ) ---
Z0 = 'Z0'                    # Initial stack bottom marker
S = 'S'                      # Represents an ongoing SQL statement/code block
C_ML = 'C_ML'                # Context marker for a multi-line comment
C_SL = 'C_SL'                # Context marker for a single-line comment
STR_S = 'STR_S'              # Context marker for single-quoted string
STR_D = 'STR_D'              # Context marker for double-quoted string
POP = 'POP'                  # Special symbol used in the action list to signify 'pop'

# --- Action Name Definitions (Translator Mode) ---
A_NULL = 'A_NULL'            # No execution action required
A_CopyBuffer = 'A_CopyBuffer'    # Copy token content to statement buffer
A_OutputCode = 'A_OutputCode'    # Finalize buffer, classify as CODE, and clear
A_OutputCmmt = 'A_OutputCmmt'    # Finalize buffer, classify as CMMT, and clear


# --- Transition Table (δ) ---
# Key: (Current_State, Input_Token_Type, Stack_Top)
# Value: (New_State, Stack_Action_List, Action_Name)
#
# Stack_Action_List: [] for NONE, [Symbol] for PUSH, [POP] for POP

PDA_TRANSITIONS = {
	# --- STARTING NEW STATEMENTS (Z0 context) ---
	(Q_START, 'CONTENT_CHUNK', Z0): (Q_CODE, [S], A_CopyBuffer),
	(Q_START, 'BEGIN_CMMT_ML', Z0): (Q_CMMT_ML, [C_ML], A_NULL),
	(Q_START, 'BEGIN_CMMT_SL', Z0): (Q_CMMT_SL, [C_SL], A_NULL),
	
	# --- CODE CONTEXT (S on stack) ---
	# Accumulate code
	(Q_CODE, 'CONTENT_CHUNK', S): (Q_CODE, [], A_CopyBuffer),
	
	# Begin nested comment contexts
	(Q_CODE, 'BEGIN_CMMT_ML', S): (Q_CMMT_ML, [C_ML], A_NULL),
	(Q_CODE, 'BEGIN_CMMT_SL', S): (Q_CMMT_SL, [C_SL], A_NULL),
	
	# Begin string quote contexts
	(Q_CODE, 'QUOTE_S', S): (Q_STR_S, [STR_S], A_CopyBuffer),
	(Q_CODE, 'QUOTE_D', S): (Q_STR_D, [STR_D], A_CopyBuffer),
	
	# End statement (main goal)
	(Q_CODE, 'SEMICOLON', S): (Q_START, [POP], A_OutputCode),
	
	# EOF on code means final output
	(Q_CODE, 'EOF', S): (Q_ACCEPT, [POP], A_OutputCode),

	# --- MULTI-LINE COMMENT CONTEXT (C_ML on stack) ---
	# Accumulate comment content (non-ending chunk)
	(Q_CMMT_ML, 'CONTENT_CHUNK', C_ML): (Q_CMMT_ML, [], A_CopyBuffer),
	
	# Ignore all other delimiters inside ML comment (e.g., Q_STR_S, BEGIN_CMMT_ML)
	(Q_CMMT_ML, 'QUOTE_S', C_ML): (Q_CMMT_ML, [], A_CopyBuffer),
	(Q_CMMT_ML, 'BEGIN_CMMT_SL', C_ML): (Q_CMMT_ML, [], A_CopyBuffer),

	# End ML comment (pop the C_ML marker) -> Returns to previous context (S or Z0)
	(Q_CMMT_ML, 'END_CMMT_ML', C_ML): (Q_CODE, [POP], A_OutputCmmt), # Return to S
	(Q_CMMT_ML, 'END_CMMT_ML', Z0): (Q_START, [POP], A_OutputCmmt), # Return to Z0

	# --- SINGLE-LINE COMMENT CONTEXT (C_SL on stack) ---
	# Accumulate comment content (non-ending chunk)
	(Q_CMMT_SL, 'CONTENT_CHUNK', C_SL): (Q_CMMT_SL, [], A_CopyBuffer),
	
	# Ignore everything until EOL
	(Q_CMMT_SL, 'QUOTE_S', C_SL): (Q_CMMT_SL, [], A_CopyBuffer),
	
	# End SL comment -> Returns to previous context (S or Z0)
	(Q_CMMT_SL, 'EOL', C_SL): (Q_CODE, [POP], A_OutputCmmt), # Return to S
	(Q_CMMT_SL, 'EOL', Z0): (Q_START, [POP], A_OutputCmmt), # Return to Z0
	
		# --- SINGLE-QUOTED STRING CONTEXT (STR_S on stack) ---
	# Accumulate content inside the string (NOTE: no action on stack)
	(Q_STR_S, 'CONTENT_CHUNK', STR_S): (Q_STR_S, [], A_CopyBuffer),
	
	# Ignore delimiters inside the string
	(Q_STR_S, 'BEGIN_CMMT_ML', STR_S): (Q_STR_S, [], A_CopyBuffer),
	
	# Escape character handling (skip escape symbol, remain in state)
	# NOTE: Assuming the tokenizer provides an 'ESCAPED_CHAR' token for \" or \'
	(Q_STR_S, 'ESCAPED_CHAR', STR_S): (Q_STR_S, [], A_CopyBuffer),
	
	# End string (pop STR_S marker) -> Returns to Q_CODE context
	(Q_STR_S, 'QUOTE_S', STR_S): (Q_CODE, [POP], A_CopyBuffer),
	
	# --- DOUBLE-QUOTED STRING CONTEXT (STR_D on stack) ---
	# Accumulate content inside the string
	(Q_STR_D, 'CONTENT_CHUNK', STR_D): (Q_STR_D, [], A_CopyBuffer),
	
	# End string (pop STR_D marker) -> Returns to Q_CODE context
	(Q_STR_D, 'QUOTE_D', STR_D): (Q_CODE, [POP], A_CopyBuffer),

	# --- GLOBAL ACCEPT/REJECT ---
	(Q_START, 'EOF', Z0): (Q_ACCEPT, [], A_NULL),
}
