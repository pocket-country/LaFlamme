# this is the file StructDef.py
from dataclasses import dataclass
from typing import List, Optional

# Definitions used by Lexi

# TokenTypes
### Defines as constants all possible as token types emitted by the Lexer.
# Delimiters
SINGLE_QUOTE = "'"
END_STATEMENT = ";"
START_BLOCK_COMMENT = "/*"
END_BLOCK_COMMENT = "*/"
START_LINE_COMMENT = "--"

# Content and Control
NEWLINE = "\\n"
CONTENT_CHUNK = "CONTENT_CHUNK"
EOF = "EOF"

# inspector to return symbol name for token string as we no longer have .name property as not an enumerate
# !! Currently not used
import inspect

def get_constant_name(constant_value, module_alias):
	"""
	Retrieves the symbolic name (the variable name) for a constant's value 
	by iterating through the module's attributes.

	This is necessary because simple string constants do not retain 
	their variable name (like Enums do).

	Args:
		constant_value (str): The value of the constant (e.g., '/*').
		module_alias (module): The imported module (e.g., pda) to search within.

	Returns:
		str: The symbolic constant name (e.g., 'START_BLOCK_COMMENT') or 
			the value itself if not found.
	"""
	
	# Iterate through all members of the imported module
	for name, value in inspect.getmembers(module_alias):
		
		# Check if the attribute is a constant (all caps) and not built-in (like __file__)
		# And check if the value matches the one we are looking for
		if name.isupper() and not name.startswith('__') and value == constant_value:
			return name
			
	# If no match is found, return the original value (e.g., 'hello world')
	return constant_value


# --- Stack Context Object --- Currently Not in Use
# This object is pushed onto the self.stack instead of a raw string.
@dataclass
class StackContext:
    """Holds the full context for an ongoing statement or comment."""
    
    # The actual PDA control symbol (e.g., 'G_CD', 'G_BC')
    control_symbol: str
    
    # The sequential ID for output logging (assigned when the context is created)
    sequence_id: int
    
    # The list of token values (strings) collected for this unit
    text_buffer: List[str]
    
    # The type of statement/unit being collected (e.g., 'CODE', 'CMMT')
    statement_type: str


# Token Definition (The Output of the Lexer) ---

@dataclass(frozen = True)
class Token:
    """Represents a lexical token from the source stream."""
    ttype: str
    value: str
    line: int
    column: int

    def to_test_line(self) -> str:
        """Formats the token for simple, line-by-line comparison in test files."""
        escaped_value = self.value.replace('\n', '\\n')
        return f"[{self.line}:{self.column}] {self.ttype}: \"{escaped_value}\""

# Character Stream (The Input Manager) ---

class CharacterStream:
    """
    Manages reading characters from a pre-loaded source string,
    providing index-based lookahead and tracking position.
    The design relies on 'peek' for lookahead and avoids the need for 'unread'.
    """
    def __init__(self, source_code: str):
        self.source = source_code # The entire file content as a string
        self.pos = 0               # Current reading index
        self.line = 1
        self.column = 0
        self.last_char = ''
        self.source_len = len(source_code)

    def next_char(self) -> Optional[str]:
        """Consumes and returns the next character, updating position."""
        if self.pos >= self.source_len:
            return None # EOF

        char = self.source[self.pos]
        self.pos += 1

        # Update position tracking based on the *previous* character consumed
        if self.last_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.last_char = char
        return char

    def peek(self, n: int = 1) -> Optional[str]:
        """Looks ahead 'n' characters without consuming them."""
        target_pos = self.pos + (n - 1)
        if target_pos < self.source_len:
            return self.source[target_pos]
        return None
