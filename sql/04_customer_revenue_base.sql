-- Customer-level revenue summary — base query for RFM analysis
-- Returns recency, frequency, and monetary metrics per customer

SELECT
    "Customer ID",
    "Customer Name",
    Segment,
    COUNT(DISTINCT "Order ID")                      AS Order_Count,
    ROUND(SUM(Sales), 2)                            AS Total_Revenue,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct,
    MIN("Order Date")                               AS First_Order_Date,
    MAX("Order Date")                               AS Last_Order_Date,
    JULIANDAY('2017-12-31') - JULIANDAY(MAX("Order Date")) AS Days_Since_Last_Order
FROM superstore
GROUP BY "Customer ID", "Customer Name", Segment
ORDER BY Total_Revenue DESC;
