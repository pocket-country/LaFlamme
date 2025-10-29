from dataclasses import dataclass
from typing import List, Optional
from enum import Enum 

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
    
