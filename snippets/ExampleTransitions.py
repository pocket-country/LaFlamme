# This file contains the PDA transition rules as a dictionary.
# The keys are (Current_State, Input_Token_Type, Stack_Top).
# The values are (New_State, Stack_Action, Action_Name).

# NOTE: Use your actual token types (e.g., 'DASH_DASH', 'SQL_CONTENT')
# for the Input_Token_Type slots when replacing this example data.

PDA_TRANSITIONS = {
	# --- Startup and Code Accumulation ---
	('q_start', 'BEGIN_CMMT_ML', 'Z0'): ('q_cmmt_ml', 'PUSH(C_ML)', 'A_NULL'),
	('q_start', 'BEGIN_CMMT_SL', 'Z0'): ('q_cmmt_sl', 'PUSH(C_SL)', 'A_NULL'),
	('q_start', 'CONTENT_CHUNK', 'Z0'): ('q_code', 'PUSH(S)', 'A_CopyBuffer'),
	
	# --- Inside Code Block ---
	('q_code', 'CONTENT_CHUNK', 'S'): ('q_code', 'NONE', 'A_CopyBuffer'),
	('q_code', 'BEGIN_CMMT_ML', 'S'): ('q_cmmt_ml', 'PUSH(C_ML)', 'A_NULL'),
	('q_code', 'BEGIN_CMMT_SL', 'S'): ('q_cmmt_sl', 'PUSH(C_SL)', 'A_NULL'),
	
	# --- Code Statement End (Trigger Output) ---
	('q_code', 'SEMICOLON', 'S'): ('q_start', 'POP', 'A_OutputCode'),
	('q_code', 'EOF', 'S'): ('q_accept', 'POP', 'A_OutputCode'),
	
	# --- Inside Multi-Line Comment ---
	('q_cmmt_ml', 'CONTENT_CHUNK', 'C_ML'): ('q_cmmt_ml', 'NONE', 'A_CopyBuffer'),
	('q_cmmt_ml', 'END_CMMT_ML', 'C_ML'): ('q_code', 'POP', 'A_OutputCmmt'),
	# Alternative exit from ML comment to q_start if that was the state before the comment:
	('q_cmmt_ml', 'END_CMMT_ML', 'Z0'): ('q_start', 'POP', 'A_OutputCmmt'), 

	# --- Inside Single-Line Comment ---
	('q_cmmt_sl', 'CONTENT_CHUNK', 'C_SL'): ('q_cmmt_sl', 'NONE', 'A_CopyBuffer'),
	('q_cmmt_sl', 'EOL', 'C_SL'): ('q_code', 'POP', 'A_OutputCmmt'),
	# Alternative exit from SL comment to q_start:
	('q_cmmt_sl', 'EOL', 'Z0'): ('q_start', 'POP', 'A_OutputCmmt'), 
}
