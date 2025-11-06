Select
	  Col1 -- the first column
	, Col2 as Fred -- because we like Fred
	, Col3 - is this starting to look like the mess we have at work
From DBO.Database d
Inner Join DBO.Another a 
  On d.matcher = a.matcher /* updated 10/4 NR */
Where ( moon = 'blue' )
;
