from sqlfluff.core import Linter
from sqlfluff.core.parser.segments.base import BaseSegment

# --- Configuration ---
# Use the TSQL dialect to ensure the 'batch' segment appears
LINTER = Linter(dialect="tsql")

# Sample SQL with multiple statements, comments, and a WHERE clause
SQL_CODE = """
-- File: ast_example.sql
SELECT 
    customer_id, 
    COUNT(*) AS order_count
FROM 
    dbo.orders -- inline comment
WHERE 
        order_date > '2023-01-01' 
    AND is_active = 1;
GO 
/* TSQL Batch Separator */
INSERT INTO        dbo.log (message) VALUES ('Data processed.');
"""

def walk_segment_tree(segment: BaseSegment, level: int = 0):
    """
    Recursively walks the SQLFluff segment tree using the reliable .segments property.

    This function prints the hierarchy, filtering out meta and simple whitespace 
    segments for clarity, and is the core of manual AST inspection.
    """
    
    # 1. Determine Indentation for Readability
    indent = "  " * level
    
    # 2. Skip segments that are purely structural or layout
    # This prevents the output from being cluttered with excessive whitespace segments.
    if segment.is_meta: #or segment.is_whitespace:
        return

    #if segment.is_whitespace:
    #    print(f"White Space {len(segment.raw)} characters")
    #    return


    # 3. Determine the Label to Print
    type_name = segment.type
    
    if type_name == 'keyword':
        # For keywords, show the type and the raw text
        label = f"KEYWORD: '{segment.raw.upper()}'"
    elif type_name in ('identifier', 'literal'):
        label = f"TOKEN: {segment.type.upper()} ('{segment.raw}')"
    elif type_name == 'comment':
        label = f"COMMENT: {segment.raw.strip()}"
    else:
        # For complex structural segments (file, statement, clause, expression)
        # Show the type and the total text it covers
        label = f"STRUCTURE: {type_name.upper()} (Raw Length: {len(segment.raw)})"

    # 4. Print the Segment Node
    print(f"{indent}- {label}")

    # 5. The Recursion (The 'Tree Walking' step)
    # Use the .segments property to get the list of immediate children,
    # and call the function again for each child.
    if segment.segments:
        for child in segment.segments:
            walk_segment_tree(child, level + 1)
            

# --- Main Execution ---

if __name__ == "__main__":
    
    print("--- Starting Full TSQL Parse ---")
    parsed_result = LINTER.parse_string(SQL_CODE)
    
    if parsed_result.tree is None:
        print("\nFATAL ERROR: Parsing failed. Check SQL syntax or dialect.")
    else:
        ast_root = parsed_result.tree
        print(f"\nROOT SEGMENT: {ast_root.__class__.__name__}\n")
        
        # Start the recursive walk from the root segment
        walk_segment_tree(ast_root, level=0)

        # Verification using the raw segments count
        print("\n--- Verification ---")
        print(f"Total Low-Level Tokens Found: {len(ast_root.raw_segments)}")
        
        comment_count = len(list(ast_root.recursive_crawl("comment")))
        statement_count = len(list(ast_root.recursive_crawl("statement")))
        print(f"Code Density: {comment_count} / {statement_count}")