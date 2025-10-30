OLD TRANSITION FROM JUST BEFORE WE ADDED ACTIONS

PDA_TRANSITIONS = {: Dict[Tuple[PDAState, TokenType, StackSymbol], Tuple[PDAState, List[StackSymbol]]] = {

    # -------------------------------------------------------------------------
    # INITIALIZATION and TERMINATION RULES
    # -------------------------------------------------------------------------

    # Start: Consume the first CODE_TEXT block and enter the main CODE state.
    (PDAState.S_START, TokenType.CONTENT_CHUNK, StackSymbol.Z0): 
        (PDAState.S_IN_CODE, [StackSymbol.Z0]), # No stack change, just transition state

    # Accept the statement end and return to START to look for the next statement.
    (PDAState.S_IN_CODE, TokenType.END_STATEMENT, StackSymbol.Z0):
        (PDAState.S_START, [StackSymbol.Z0]),

    # Accept EOF only when we are outside any open structure (Code state, empty stack)
    (PDAState.S_IN_CODE, TokenType.EOF, StackSymbol.Z0):
        (PDAState.S_ACCEPT, [StackSymbol.Z0]),
        
    # -------------------------------------------------------------------------
    # MAIN CODE CHUNK HANDLING (S_IN_CODE)
    # -------------------------------------------------------------------------
    
    # In code, consuming general content chunks (SQL code, whitespace)
    (PDAState.S_IN_CODE, TokenType.CONTENT_CHUNK, StackSymbol.Z0):
        (PDAState.S_IN_CODE, [StackSymbol.Z0]),

    # -------------------------------------------------------------------------
    # STRING MASKING RULES (Handles '...' escaping all delimiters)
    # -------------------------------------------------------------------------

    # Entering String Mode (from any state where a string starts)
    (PDAState.S_IN_CODE, TokenType.SINGLE_QUOTE, StackSymbol.Z0):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING, StackSymbol.Z0]), # Push String Marker
    
    # Content inside a string is consumed without affecting state/stack
    (PDAState.S_IN_STRING, TokenType.CONTENT_CHUNK, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),

    # String mode is immune to all other delimiters; they are treated as content.
    (PDAState.S_IN_STRING, TokenType.START_BLOCK_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.END_BLOCK_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.START_LINE_COMMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.NEWLINE, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),
    (PDAState.S_IN_STRING, TokenType.END_STATEMENT, StackSymbol.M_STRING):
        (PDAState.S_IN_STRING, [StackSymbol.M_STRING]),

    # Exiting String Mode (POP the String Marker)
    (PDAState.S_IN_STRING, TokenType.SINGLE_QUOTE, StackSymbol.M_STRING):
        (PDAState.S_IN_CODE, []), # Pop M_STRING, return to IN_CODE
        
    # -------------------------------------------------------------------------
    # BLOCK COMMENT NESTING RULES (/* ... */)
    # -------------------------------------------------------------------------

    # Entry to block comment (from Code state)
    (PDAState.S_IN_CODE, TokenType.START_BLOCK_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C, StackSymbol.Z0]), # Push Block Marker

    # Content inside comment (ignore content, ignore line/statement ends)
    (PDAState.S_IN_BLOCK_C, TokenType.CONTENT_CHUNK, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),
    (PDAState.S_IN_BLOCK_C, TokenType.NEWLINE, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),
    (PDAState.S_IN_BLOCK_C, TokenType.END_STATEMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C]),

    # Nested Block Comment Entry (PUSH another marker)
    (PDAState.S_IN_BLOCK_C, TokenType.START_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, [StackSymbol.M_BLOCK_C, StackSymbol.M_BLOCK_C]), # Replace M_BLOCK_C with [M_BLOCK_C, M_BLOCK_C]

    # Block Comment Exit (POP one marker)
    (PDAState.S_IN_BLOCK_C, TokenType.END_BLOCK_COMMENT, StackSymbol.M_BLOCK_C):
        (PDAState.S_IN_BLOCK_C, []), # Pop M_BLOCK_C

    # Final Block Comment Exit (POP the last marker, return to Code)
    (PDAState.S_IN_BLOCK_C, TokenType.END_BLOCK_COMMENT, StackSymbol.Z0): # Error case, should not happen if stack used correctly
        (PDAState.S_IN_CODE, [StackSymbol.Z0]),
        
    # -------------------------------------------------------------------------
    # LINE COMMENT RULES (-- to \n)
    # -------------------------------------------------------------------------

    # Entry to line comment (from Code state)
    (PDAState.S_IN_CODE, TokenType.START_LINE_COMMENT, StackSymbol.Z0):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C, StackSymbol.Z0]), # Push Line Marker
        
    # Content inside line comment (ignore content)
    (PDAState.S_IN_LINE_C, TokenType.CONTENT_CHUNK, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
        
    # Line comments ignore all other delimiters except NEWLINE
    (PDAState.S_IN_LINE_C, TokenType.START_BLOCK_COMMENT, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
    (PDAState.S_IN_LINE_C, TokenType.END_BLOCK_COMMENT, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
    (PDAState.S_IN_LINE_C, TokenType.SINGLE_QUOTE, StackSymbol.M_LINE_C):
        (PDAState.S_IN_LINE_C, [StackSymbol.M_LINE_C]),
        
    # Line Comment Exit (POP the line marker, return to Code)
    (PDAState.S_IN_LINE_C, TokenType.NEWLINE, StackSymbol.M_LINE_C):
        (PDAState.S_IN_CODE, []), # Pop M_LINE_C

    # -------------------------------------------------------------------------
    # ERROR HANDLING (Any transition not defined above is an implicit error)
    # -------------------------------------------------------------------------

    # (Add explicit error state rules here later)
}
