# Assuming you have already defined self.next_sequence_id = 1 in __init__
# and imported the necessary constants:
# from ParseDef import A_None, A_CopyBuffer, A_OutputCode, A_OutputCmmt
# from StructDef import StackContext

def _create_new_context(self, control_symbol_string, action_name):
    """
    Creates a new StackContext object for a PUSH action, assigning its 
    sequence ID and statement type based on the context being entered.

    Args:
        control_symbol_string (str): The new stack symbol (e.g., pda.G_CD).
        action_name (str): The action from the transition rule.
    
    Returns:
        StackContext: The initialized object.
    """
    
    # Determine the statement type for the new context
    if control_symbol_string == pda.G_Z0 or control_symbol_string == pda.G_CD:
        current_type = 'CODE'
    else: # G_BC, G_LC, G_STR, etc.
        current_type = 'CMMT'
        
    # Sequence ID Logic: Only assign a new ID if it's the start of a top-level code block.
    # We use a mutable list for the buffer.
    
    new_context = StackContext(
        control_symbol=control_symbol_string,
        sequence_id=self.next_sequence_id, # Inherit or assign the current global ID
        text_buffer=[],
        statement_type=current_type
    )
    
    return new_context

# NOTE: You will need a separate, public method to handle the A_IncrementSeq action.
def increment_sequence_id(self):
    """Increments the global sequence ID after a statement is successfully output."""
    self.next_sequence_id += 1
