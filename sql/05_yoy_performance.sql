-- Year-over-year revenue, profit, and margin trend
-- Supports executive summary finding that margin dipped in 2017

SELECT
    STRFTIME('%Y', "Order Date")                    AS Order_Year,
    COUNT(*)                                        AS Transactions,
    COUNT(DISTINCT "Customer ID")                   AS Unique_Customers,
    ROUND(SUM(Sales), 2)                            AS Total_Revenue,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2)        AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct
FROM superstore
GROUP BY Order_Year
ORDER BY Order_Year ASC;
