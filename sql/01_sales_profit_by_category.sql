-- Sales and profit performance by category
-- Identifies which product categories drive revenue vs profitability

SELECT
    Category,
    COUNT(*)                                        AS Transactions,
    ROUND(SUM(Sales), 2)                            AS Total_Sales,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2)        AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct,
    SUM(CASE WHEN Profit < 0 THEN 1 ELSE 0 END)     AS Loss_Transactions,
    ROUND(
        SUM(CASE WHEN Profit < 0 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2
    )                                               AS Loss_Rate_Pct
FROM superstore
GROUP BY Category
ORDER BY Total_Sales DESC;
