-- Discount rates and profit loss analysis by region
-- Supports finding that Central region over-discounts relative to peers

SELECT
    Region,
    COUNT(*)                                            AS Transactions,
    ROUND(AVG(Discount) * 100, 2)                       AS Avg_Discount_Pct,
    ROUND(SUM(Profit), 2)                               AS Total_Profit,
    ROUND(AVG(Profit), 2)                               AS Avg_Profit_Per_Txn,
    SUM(CASE WHEN Discount >= 0.3 THEN 1 ELSE 0 END)    AS High_Discount_Txns,
    ROUND(SUM(CASE WHEN Profit < 0 THEN Profit ELSE 0 END), 2) AS Total_Loss_Amount,
    ROUND(
        SUM(CASE WHEN Profit < 0 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2
    )                                                   AS Loss_Rate_Pct
FROM superstore
GROUP BY Region
ORDER BY Avg_Discount_Pct DESC;
