# ## reconfigured stack action processing more clunky but explicit for possible integration
# This function or method logic assumes the following:
# 1. 'self.stack' is a Python list/array representing the PDA stack.
# 2. 'EPSILON' constant is defined and accessible (e.g., from pda_frozen_transitions).
# 3. 'transition_result' is the tuple: (new_state, stack_action_list, action_name).

def process_stack_action(self, transition_result):
	# Unpack the stack action list
	stack_action_list = transition_result[1]
	
	# --- 1. POP/EPSILON Action ---
	if stack_action_list == [EPSILON]:
		# This is the theoretical delta -> (q', epsilon) action.
		if self.stack:
			self.stack.pop()
		else:
			# Should never happen in a correct grammar, but handles error state.
			print("PDA ERROR: Attempted to pop EPSILON from an empty stack!")
			# self.trigger_reject()

	# --- 2. NONE/DO NOTHING Action ---
	elif stack_action_list == []:
		# This is the theoretical delta -> (q', X) action (consume input, leave X).
		# Stack remains completely unchanged.
		return

	# --- 3. PUSH Action ---
	elif len(stack_action_list) == 1:
		# This is the theoretical delta -> (q', X Y) action (push Y onto X).
		# We must ensure we aren't accidentally trying to push EPSILON here.
		symbol_to_push = stack_action_list[0]
		
		if symbol_to_push != EPSILON:
			self.stack.append(symbol_to_push)
		else:
			# Handles the logic error of a list containing only EPSILON
			print("PDA ERROR: Misconfigured PUSH action attempted to push EPSILON.")
			# self.trigger_reject()
			
	# --- 4. Malformed Action List ---
	else:
		# Handles cases like lists with multiple elements (e.g., ['A', 'B']) 
		# which are not supported by this simple PDA structure.
		print(f"PDA ERROR: Malformed stack action list in rule: {stack_action_list}")
		# self.trigger_reject()
