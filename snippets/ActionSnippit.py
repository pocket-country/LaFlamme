# --- Setup: Define the Action Map ---
# This dictionary maps the Action Name string to the actual function reference.

def copy_to_buffer(token):
	# Assumes 'self.statement_buffer' is a list
	self.statement_buffer.append(token.value)

def output_statement(classification):
	# Assumes 'self.statement_buffer' is a list
	processed_text = "".join(self.statement_buffer).strip()
	
	if processed_text:
		# Replace 'print' with your file-writing logic
		print(f"[{classification}]: {processed_text}")
	
	self.statement_buffer.clear()

# Helper function to wrap the output_statement with classification
def output_code(token):
	output_statement("CODE")

def output_cmmt(token):
	output_statement("CMMT")

# The Action Map
ACTION_MAP = {
	"A_CopyBuffer": copy_to_buffer,
	"A_OutputCode": output_code,
	"A_OutputCmmt": output_cmmt,
	"A_NULL": lambda token: None # Null action does nothing
}


# --- Transition Logic Integration ---
# This code snippet belongs inside your main PDA loop, right after
# you successfully look up the transition rule tuple.

	# token is the current token being processed (must be passed to actions)
	# transition_rule is the tuple: (new_state, stack_action, action_name)
	
	# ... (Existing logic for looking up transition_rule) ...
	
	if transition_rule:
		# Unpack the rule to get the action name
		new_state, stack_action, action_name = transition_rule
		
		# Execute the action before updating state/stack (usually done first)
		if action_name in ACTION_MAP:
			ACTION_MAP[action_name](token) # Pass the current token to the action function
		else:
			# Safety check for unhandled action names
			raise ValueError(f"Unknown PDA action: {action_name}")
			
		# Apply the state and stack changes
		self.current_state = new_state
		# ... (Logic to handle PUSH/POP/NONE based on stack_action) ...
		
	else:
		# ... (Existing logic for Reject/Error handling) ...