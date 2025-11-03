# Monica.py --- holds our tracing/logging class & associated
import uuid
import csv
from typing import List, Tuple, Any
import os
import datetime
import hashlib

# full path to the python source code holding parser definitions
# hardwire it, baby!
PARSER_DEF = os.path.join(SCRIPT_DIR, "support", "ParseDef.py")

# folder, relitive to main program, of directory holding log files
LOG_FILE_STORE = tracing/logs

# folder, relative to main program dir, of directory holding file objects (named with hash)
OBJ_FILE_STORE = tracing/objects

class TransTrace:
    """
    A simple implement transition traceing for a single parser run.
    (Includes file management functions)
    """
  
    def __init__(self, base_dir, source_file_name):
        
        # Set some state!    
        # this stores transitions as list items, built via record calls
        self.transition_buffer = []
        
        # These fields uniquely identify a 'run' - a pointer to the PDA file, a pointer to the source code being proceed and the run time
        # These fields will be written as a header line to the transcaction trace log file
        # and used to build a log filename.  Maybe we don't need the first to to be instance variables
        self.definition_id = ""
        self.source_id = ""
        self.start_timestamp = datetime.datetime.now()
        self.end_timestamp = ""
        
        # a handy timesaver to flag the run as successful or not without having to read to the end of the log
        self.success = False
        
        # we will build the full path version of the log filename in the init function and use in a couple of places.
        self.log_path = ""
        
        # Do some work.  My AI assures me that Pythonistas are going to hate this, I am supposed to have a 
        # tangled pumpkin patch of _helper() functions rather than just laying out the work and plowing through it.
        
        # hash files to create object filenames and copy contents to object files in storage director

        # Save definitions - because file is used in imports we assume it exists cause code hasn't crashed
        with open(PARSER_DEF, 'r') as f:
            # ... read the file ...    
            file_content = f.read()
        
        self.definition_id = hash_file(file_content)
        definition_file = os.path.join(SCRIPT_DIR, DEFINITION_STORE, f"{self.definition_id}.pda") 

        if not(os.path.exists(definition_file)):
            # we havent seen this set of PDA transitions before ... 
            try:
                with open(definition_file, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            xcept Exception as e:
                print(f"Error writing PDA definintion object file: {e}")
                
        # Save source code - existence verified elsewhere (we hope)
        # unlike the definition file this needs to be the full path (cause could be anywhere)
        with open( source_file, 'r') as f:
            file_content = f.read()
        
        self.source_id = hash_file(file_content)
        definition_file = os.path.join(SCRIPT_DIR, DEFINITION_STORE, f"{self.source_id}.src") 

        if not(os.path.exists(definition_file)):
            # we havent seen this set of PDA transitions before ... 
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            except Exception as e:
                print(f"Error writing source code object file: {e}")        
                
        # now, just for fun, lets initialize the log file with the header line
        # Build unique filename (Timestamp + UUID)
        timestamp_prefix = self.timestamp.strftime("%Y%m%d-%H%M%S-%f")
        unique_suffix = uuid.uuid4().hex[:6]
        log_filename = f"{timestamp_prefix}-{unique_suffix}.dat"
        
        self.log_path = os.path.join(SCRIPT_DIR, LOG_FILE_STORE, log_filename)
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                # doing basic roll 'yer own csv.  I know none of the fields have commas.
                f.write(self.start_timestamp.isoformat)
                f.write(',')
                f.write(self.definition_id)
                f.write(',')
                f.write(self.source_id)
        except Exception as e:
            print(f"Error initializing log file: {e}")
        
        # Groovy, all that is taken care of
          
    def _normalize_action_value(action_tuple):
        """Replaces function references in the action tuple with stable strings."""
        # Assuming action_tuple = (<next_state>, <stack_action>, <execution_action>)
        # The execution_action (index 2) is the function reference.
        
        # Get the function's name string:
        func_name = action_tuple[2].__name__ if callable(action_tuple[2]) else str(action_tuple[2])
        
        # Return the new tuple with the name instead of the reference
        return action_tuple[0], action_tuple[1], func_name
        
    def _hash_file(file_content: str) -> str:
    """
    Generates a stable SHA-256 hash of file content.
   
    Returns:
        str: The SHA-256 hash.
    """
    hasher = hashlib.sha256()
    hasher.update(file_content.encode('utf-8')
    return hasher.hexdigest()    


    def record_transition(self, trigger_key, action_value, success = True):
        """Records a single transition (real or ghost) to the buffer."""
        # Ensure trigger_key is represented as a string for storage
        trigger_str = str(trigger_key) 
        
        if success:
            status = "Next"
            normalized_action = _normalize_action_value(action_value)
        else:
            status = "Fail"
            normalized_action = action_value
            
        self.transition_buffer.append((
            'trigger': trigger_str,
            'action': normalized_action,
            'result': status
        ))
    
   
    def write_transitions(self):
        try:
            with open(self.log_path, 'a', encoding = 'utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                for trigger, action, result in self.transition_buffer:
                    row = [
                        *trigger
                        *action
                        result
                    ]
                writer.writerow(row)
        except Exception as e:
            print(f"Error appending to log file: {e}")

    #End class def.  No main block code ATM, nor init function

