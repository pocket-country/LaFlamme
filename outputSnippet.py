# Assuming this is part of your parser class, 'self' references instance variables.

# File path to write the output
OUTPUT_FILE_PATH = "processed_statements.txt"
# A static file handle that can be opened once (if Godot allows it, otherwise
# you might open/close on each write, or manage the handle in the main loop).
# For simplicity, we'll use a basic append-write approach here.

def output_statement(classification):
	# 1. Join accumulated parts
	# NOTE: The .strip() cleans up any leading/trailing whitespace from token accumulation
	processed_text = "".join(self.statement_buffer).strip() 
	
	# 2. Check for content and format the output
	if processed_text: 
		# Format: [CLASSIFICATION] processed_text
		output_line = f"[{classification}]: {processed_text}\n"
		
		# 3. Write to the output file (using Python's append mode 'a')
		try:
			# In a practical application, you'd manage this file handle outside
			# the loop, but this simple structure is effective.
			with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f:
				f.write(output_line)
			
			# Optional: Log the action for debugging
			# print(f"WROTE: {output_line.strip()}")
			
		except IOError as e:
			print(f"ERROR writing to output file {OUTPUT_FILE_PATH}: {e}")
			
	# 4. Clear buffer for the next statement/comment
	self.statement_buffer.clear()