-- Ths is ast_example.sql
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