-- Top and bottom sub-categories by total profit
-- Identifies Tables as the single largest loss-making product line

SELECT
    Category,
    "Sub-Category",
    COUNT(*)                                        AS Transactions,
    ROUND(SUM(Sales), 2)                            AS Total_Sales,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2)        AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct
FROM superstore
GROUP BY Category, "Sub-Category"
ORDER BY Total_Profit ASC;
