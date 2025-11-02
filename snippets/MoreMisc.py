
## Currently Unused
def _normalize_action_value(action_tuple):
    """
    Safely converts a rule action tuple (which may contain function references)
    into a tuple suitable for hashing and JSON serialization.
    """
    # The execution_action is at index 2 (the function reference)
    execution_action = action_tuple[2]
    
    # Use the ternary operator to extract a stable string representation
    func_name = execution_action.__name__ if callable(execution_action) else str(execution_action)
    
    # Return the new tuple: (next_state, stack_action, func_name)
    return action_tuple[0], action_tuple[1], func_name

# --- Configuration Snapshot Manager ---

def save_ruleset_snapshot(ruleset_hash, transition_dict):
    """
    Saves the full, normalized ruleset to a file named by its hash.
    Only writes the file if the hash is new (the file doesn't exist).
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    filepath = os.path.join(CONFIG_DIR, f"{ruleset_hash}.json")
    
    if os.path.exists(filepath):
        # Hash is already known; snapshot exists. Nothing to do.
        return False 

    # 1. Normalize the full dict for stable JSON output
    normalized_data = {}
    for key_tuple, value_tuple in transition_dict.items():
        # Keys must be strings for JSON, so convert the trigger tuple to a string
        key_str = str(key_tuple) 
        
        # Normalize the action value (remove function reference)
        value_normalized = _normalize_action_value(value_tuple)
        
        # Convert the resulting value tuple to a list for JSON serialization
        normalized_data[key_str] = list(value_normalized)

    # 2. Write the JSON file
    try:
        with open(filepath, 'w') as f:
            json.dump(normalized_data, f, indent=4)
        print(f"\n[Trace] Saved NEW ruleset snapshot: {ruleset_hash}.json")
        return True
    except Exception as e:
        print(f"\n[Trace ERROR] Could not save snapshot {ruleset_hash}: {e}")
        return False
