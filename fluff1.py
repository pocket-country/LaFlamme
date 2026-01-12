# seeing what SQLFluff can do
from typing import Any, Iterator, Union

import sqlfluff
import json


test_query = "with cte as(select col1, col2 from src.first UNION select a as col1, b as col2 from src.second) select * into dbo.result from cte;"

parse_result = sqlfluff.parse(test_query, dialect = 'tsql')

print(parse_result)

with open("/Users/WRobb/LaFlamme/fluff1.json", 'w') as f:
    json.dump(parse_result, f, indent = 4)
    

