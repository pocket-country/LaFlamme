from dataclasses import dataclass
from typing import List, Optional

# --- 1. Token Definition (The Output of the Lexer) ---

@dataclass(frozen=True)
class Token:
    """Represents a lexical token from the source stream."""
    type: str     # e.g., 'START_BLOCK_COMMENT', 'CONTENT_CHUNK', 'END_STATEMENT'
    value: str    # The exact string matched, e.g., '/*', 'SELECT...'
    line: int
    column: int
    
    def to_test_line(self) -> str:
        """Formats the token for simple, line-by-line comparison in test files."""
        # Escape newlines within the token value for single-line output
        escaped_value = self.value.replace('\n', '\\n')
        return f"[{self.line}:{self.column}] {self.type}: \"{escaped_value}\""

# --- 2. Character Stream (The Input Manager) ---

class CharacterStream:
    """
    Manages reading characters from a file, providing lookahead (peek) 
    and tracking position for error reporting.
    """
    def __init__(self, filename: str):
        # We assume the file is correctly handled by the calling program
        self.file = open(filename, 'r')
        self.buffer: List[str] = [] # The lookahead buffer (stores characters)
        self.line = 1
        self.column = 0
        self.last_char = ''
        
    def next_char(self) -> Optional[str]:
        """Consumes and returns the next character, updating position."""
        
        # 1. Get the character (from buffer or file)
        if self.buffer:
            char = self.buffer.pop(0)
        else:
            char = self.file.read(1)
            
        if not char:
            self.file.close()
            return None # EOF

        # 2. Update position tracking based on the *previous* character read
        if self.last_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.last_char = char
        return char

    def peek(self, n: int = 1) -> Optional[str]:
        """Looks ahead 'n' characters without consuming them."""
        # Pre-fill the buffer if necessary
        while len(self.buffer) < n:
            char = self.file.read(1)
            if not char:
                break # EOF reached
            self.buffer.append(char)
            
        if len(self.buffer) >= n:
            # Note: buffer is 0-indexed, so the nth character is at index n-1
            return self.buffer[n-1]
        return None
    
    def unread(self, char: str):
        """Puts a character back onto the stream buffer. Used when a lookahead fails."""
        self.buffer.insert(0, char)
        # We rely on this being called immediately after a failed peek, 
        # so we do not need to adjust line/column counters here.
