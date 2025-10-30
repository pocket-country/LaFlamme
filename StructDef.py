from dataclasses import dataclass
from typing import List, Optional
from enum import Enum 

## Definitions used by Lexi

# Token Type Definition (ENUM) ---

class TokenType(Enum):
    """Defines all possible token types emitted by the Lexer."""
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

# Token Definition (The Output of the Lexer) ---

@dataclass(frozen=True)
class Token:
    """Represents a lexical token from the source stream."""
    type: TokenType  
    value: str       
    line: int
    column: int
    
    def to_test_line(self) -> str:
        """Formats the token for simple, line-by-line comparison in test files."""
        escaped_value = self.value.replace('\n', '\\n')
        return f"[{self.line}:{self.column}] {self.type.name}: \"{escaped_value}\""

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
    
## Definitions used by Pedro
# --- PDA State Definitions ---
# These represent the nodes in the state machine.
Q_START = 'q_start'      # Ready for a new statement or comment
Q_CODE = 'q_code'        # Currently processing SQL code
Q_CMMT_ML = 'q_cmmt_ml'  # Currently inside a multi-line comment (/* ... */)
Q_CMMT_SL = 'q_cmmt_sl'  # Currently inside a single-line comment (--)
Q_ACCEPT = 'q_accept'    # Final state reached upon EOF (Accept)


# --- Stack Symbol Definitions ---
# These are the non-terminals used by the PDA for context tracking.
Z0 = 'Z0'                # Initial stack bottom marker
S = 'S'                  # Symbol for an ongoing SQL statement/code block
C_ML = 'C_ML'            # Symbol for an ongoing multi-line comment context
C_SL = 'C_SL'            # Symbol for an ongoing single-line comment context


# --- Stack Action Definitions ---
# These are instructions for the parser's stack operation.
PUSH_PREFIX = 'PUSH'
POP = 'POP'
NONE = 'NONE'


# --- Action Name Definitions (Translator Mode) ---
# These are strings mapped to executable functions in the parser's action handler.
A_NULL = 'A_NULL'          # No action required
A_CopyBuffer = 'A_CopyBuffer'  # Append token content to the statement buffer
A_OutputCode = 'A_OutputCode'  # Finalize statement buffer and classify as CODE
A_OutputCmmt = 'A_OutputCmmt'  # Finalize statement buffer and classify as CMMT
