# compute some basic code review metrics for an input SQL file

import os
import sys

from typing import List, Tuple, Dict, Optional, Union, TextIO, Any

from sqlfluff.core import Linter
from sqlfluff.core.parser.segments.base import BaseSegment

def count_lines(ftxt: str) -> int:
    return ftxt.count('\n')
    
def count_chars(ftxt: str)-> int:
    return len(ftxt.replace('\n', ''))
    
def parse_it(ftxt: str) -> BaseSegment:
    a_linter = Linter(dialect = "tsql")
    result_ast = a_linter.parse_string(ftxt)
    ast_root = result_ast.tree
    return ast_root
    
def count_statements(ast: BaseSegment) -> int:
    return len(list(ast.recursive_crawl("statement")))
    
def count_comments(ast: BaseSegment) -> int:
   return len(list(ast.recursive_crawl("comment")))

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Usage: python CRMetrics.py <input_file.sql>")
    else:
        input_filename = sys.argv[1]

    try:
        with open(input_filename, 'r', encoding = 'utf-8') as f:
            source_code = f.read()        
        print(f"CRMetrics: SQL Source File {input_filename} Read")    
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    lines = count_lines(source_code)
    chars = count_chars(source_code)
    
    ast = parse_it(source_code)
    
    comments = count_comments(ast)
    statements = count_statements(ast)
    
    print(f"Source file {input_filename} contains {chars} characters in {lines} lines ")
    print(f"SQL code includes {comments} comments and {statements} statements")
    
