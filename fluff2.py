# seeing what SQLFluff can do
from typing import Any, Iterator, Union
from sqlfluff.core import Linter
from collections import defaultdict
import json

#test_query = "with cte as(select col1, col2 from src.first UNION select a as col1, b as col2 from src.second) select * into dbo.result from cte;"

test_query = """
-- File: ast_example.sql
SELECT 
    customer_id, 
    COUNT(*) AS order_count
FROM 
    dbo.orders -- inline comment
WHERE 
    order_date > '2023-01-01' 
    AND is_active = 1
GO 
/* TSQL Batch Separator */
INSERT INTO dbo.log (message) VALUES ('Data processed.')
"""
a_linter = Linter(dialect = "tsql")
result_ast = a_linter.parse_string(test_query)
ast_root = result_ast.tree

print("--- AST Object (For Code Manipulation) ---")
print(f"AST Root Type: {ast_root.__class__.__name__}")

all_raw_segments = ast_root.raw_segments
#print(ast_root.raw_segments)

comment_set = list(ast_root.recursive_crawl("comment"))
print(len(comment_set))
for i, s in enumerate(comment_set):
    print(f"{i}: {s.raw}")
    
statement_set = list(ast_root.recursive_crawl("statement"))
print(len(statement_set))
for s in statement_set:
    print(s.raw)
    print(list(s.segments))
    

#for i in range(5):
#    segment = ast_root.raw_segments[i]
#        
#   # Access the properties directly on the segment object
#    seg_type = segment.type
#    seg_text = segment.raw
#    
#    # Access the properties on the pos_marker sub-object
#    line = segment.pos_marker.line_no
#    col = segment.pos_marker.line_pos
#    
#    print(f"Index {i}:")
#    print(f"  Type: {seg_type}")
#    print(f"  Text: '{seg_text.strip()}'")
#    print(f"  Position: L{line}, P{col}")

counts = defaultdict(int)

for i in range(len(list(all_raw_segments))):
    segment = all_raw_segments[i].type
    counts[segment] += 1
    
print(counts)



# this works >> segments = ast_root.recursive_crawl("statement")
#print(f"Total Segments: {len(list(segments))}")

#readable_dict = ast_root.as_dict()

#print(f"Dictionary Keys: {readable_dict.keys()}")

#print("\n--- Formatted JSON Output ---")
#print(json.dumps(readable_dict, indent=2))


#print(parse_result)

#with open("/Users/WRobb/LaFlamme/fluff1.json", 'w') as f:
#    json.dump(parse_result, f, indent = 2)
    

