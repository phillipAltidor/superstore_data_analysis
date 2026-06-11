# Superstore Business Performance Analysis
## Executive Report — 2014–2017

---

## Objective

Analyze four years of Superstore transactional data to identify the root causes of profit underperformance, quantify the business impact, and deliver actionable recommendations with defined next validation steps.

**Dataset:** 9,993 transactions | 793 customers | 3 categories | 4 regions | 2014–2017

---

## Key Performance Indicators

| Metric | Value |
|---|---|
| Total Revenue | $2,296,919 |
| Total Profit | $286,409 |
| Overall Profit Margin | 12.47% |
| Total Customers | 793 |
| Inactive / Low Value Customers | 351 (44.3%) |

---

## Finding 1: Over-Discounting is a Major Measurable Driver of Profit Loss

**Evidence:**
- Discount is a statistically significant negative predictor of profit (OLS regression, p < 0.0001)
- Controlled estimate: a 10 percentage-point increase in discount is associated with **~$23.63 lower profit per transaction**, holding Category, Region, Sales, and Quantity constant
- Welch's t-test confirms the profit difference between low-discount and high-discount groups is not due to chance (p < 0.0001)
- Mean profit: **$49.04** for transactions under 30% discount vs **-$97.24** for 30%+ discount
- 1,392 transactions (14% of all sales) at 30%+ discount generated **-$135,364 in net losses**

**Business Impact Scenarios (if 20% discount cap is piloted):**

| Scenario | Assumption | Estimated Recoverable Profit |
|---|---|---|
| Conservative | Minimal volume disruption | ~$34,600 |
| Base Case | Some price-sensitive customers lost | ~$69,200 |
| Aggressive | Significant volume retained | ~$103,800 |

*Note: These are scenario estimates. Volume impact must be validated via A/B test or regional pilot before projecting company-wide.*

---

## Finding 2: Furniture Margin Collapse — Concentrated in Tables

**Evidence:**
- Furniture generates $741K in revenue but only **2.49% profit margin** (vs 17.4% for Technology)
- Tables sub-category: **-$17,725 total profit** — the worst performing product line
- Bookcases: **-$3,472 total profit**
- 1 in 3 Furniture transactions loses money (33.6% loss rate)
- Furniture carries the highest average discount rate at 17.39%

**Recommendation:** Conduct SKU-level pricing review on Tables. Assess whether margin can be recovered through price increases or discount restrictions before considering discontinuation.

---

## Finding 3: Customer Retention Crisis

**Evidence:**
- 44.3% of customers are Inactive / Low Value (last purchased significantly before reference date)
- At Risk + Cannot Lose segments: 134 customers representing **$530K in revenue** showing disengagement
- Champions (34 customers) average **$5,863 spend** — highest value, most recently active
- Loyal customers (142) average **$4,250 spend** and bought within the last 37 days on average

**Recommendation:** Prioritize retention over acquisition. The cost of winning back a lapsed customer is lower than acquiring a new one.

---

## Strategic Recommendations

| Priority | Action | Target | Expected Impact | Confidence | Next Validation |
|---|---|---|---|---|---|
| High | Pilot 20% discount cap in Central region | Central region sales team | Protect margin on high-discount orders | Medium | Compare margin before/after one quarter |
| High | Launch At Risk / Cannot Lose retention campaign | 134 customers | Protect $530K in at-risk revenue | Medium | Track repeat purchase rate and margin lift |
| Medium | Tables SKU-level pricing review | Furniture category | Address -$17,725 total loss (2014–2017) | High | Review price/discount rules per SKU |
| Medium | Audit Central discount approval process | Regional managers | Central discounts 24% vs West 11% | High | Compare discount approval rates by region |
| Low | Build Champion VIP program | 34 Champion customers | Protect $199K top-tier revenue | Medium | Track retention rate and spend trend |
| Low | New customer onboarding sequence | 159 New customers | Drive second purchase conversion | Low | Track 90-day repeat purchase rate |

---

## Risks & Assumptions

1. **Discount removal may reduce volume** — some customers are price-sensitive. The controlled regression estimates the profit-discount relationship but cannot predict volume elasticity. A pilot is required before scaling.
2. **RFM segments are based on historical data** — the "Inactive" classification reflects purchase recency relative to December 2017. Some customers may have churned for reasons unrelated to retention strategy (relocation, business closure).
3. **Regression R² = 0.28** — the model explains 28% of profit variation. Other factors (cost of goods, logistics, contract terms) are not captured in this dataset and may affect the true relationship.
4. **Tables losses may be strategic** — Tables could serve as a loss leader driving other profitable purchases. This should be tested before any discontinuation decision.

---

## Next Validation Steps

1. Run a one-quarter regional pilot capping discounts at 20% in Central region
2. Pull customer-level data on Tables buyers — do they purchase other profitable items in the same order?
3. Build a cohort analysis on New Customers to measure 90-day repeat purchase rate
4. Rerun this analysis after Q1 2018 data is available to confirm margin trend

---

*Analysis conducted using Python (pandas, statsmodels, scipy, matplotlib, seaborn). All notebooks and supporting outputs are available in the project repository.*
