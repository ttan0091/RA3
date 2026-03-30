---
name: creating-financial-models
description: Build financial models for startups, business cases, revenue forecasting, unit economics, and investment analysis. Includes templates and formulas.
version: 1.0.0
author: Perry
---

# Financial Modeling Skill

You are a financial analyst who helps build models for business planning, fundraising, and strategic decision-making.

## Core Concepts

### Types of Financial Models

1. **Three Statement Model** - Income statement, balance sheet, cash flow
2. **DCF (Discounted Cash Flow)** - Valuation based on future cash flows
3. **SaaS Metrics Model** - MRR, churn, LTV, CAC for subscription businesses
4. **Unit Economics Model** - Per-customer profitability analysis
5. **Scenario Analysis** - Best/base/worst case projections

## SaaS Financial Model

### Key Metrics

```markdown
## Monthly Metrics Dashboard

### Revenue
- MRR (Monthly Recurring Revenue): $[X]
- ARR (Annual Recurring Revenue): MRR × 12 = $[Y]
- Net New MRR: New MRR + Expansion MRR - Churned MRR

### Growth
- MoM Growth Rate: (Current MRR - Previous MRR) / Previous MRR
- Net Revenue Retention (NRR): (Starting MRR + Expansion - Churn) / Starting MRR

### Customer Metrics
- Total Customers: [X]
- New Customers: [X]
- Churned Customers: [X]
- Logo Churn Rate: Churned / Starting Customers
- Revenue Churn Rate: Churned MRR / Starting MRR
```

### Unit Economics

```markdown
## Unit Economics

### Customer Acquisition Cost (CAC)
CAC = Total Sales & Marketing Spend / New Customers Acquired

Example: $50,000 / 100 customers = $500 CAC

### Lifetime Value (LTV)
LTV = ARPU × Gross Margin × Average Customer Lifetime

Where:
- ARPU = Average Revenue Per User (monthly)
- Gross Margin = (Revenue - COGS) / Revenue
- Customer Lifetime = 1 / Monthly Churn Rate

Example: $100 × 80% × 24 months = $1,920 LTV

### LTV:CAC Ratio
Target: > 3:1 (healthy business)
Warning: < 1:1 (losing money on each customer)

Example: $1,920 / $500 = 3.84:1 ✅

### Payback Period
Months to recover CAC = CAC / (ARPU × Gross Margin)

Example: $500 / ($100 × 80%) = 6.25 months
```

### MRR Waterfall

```markdown
## MRR Waterfall - [Month]

| Component | Amount | % of Starting |
|-----------|--------|---------------|
| Starting MRR | $100,000 | 100% |
| + New MRR | $15,000 | 15% |
| + Expansion MRR | $8,000 | 8% |
| - Churned MRR | -$5,000 | -5% |
| - Contraction MRR | -$2,000 | -2% |
| **= Ending MRR** | **$116,000** | **116%** |

Net New MRR: $16,000
MoM Growth: 16%
```

## Revenue Forecasting

### Bottoms-Up Model

```markdown
## Revenue Forecast (Bottoms-Up)

### Assumptions
- Starting customers: 500
- Monthly new customer growth: 10%
- Monthly churn: 3%
- ARPU: $99

### 12-Month Projection

| Month | Starting | New | Churned | Ending | MRR |
|-------|----------|-----|---------|--------|-----|
| 1 | 500 | 50 | 15 | 535 | $52,965 |
| 2 | 535 | 54 | 16 | 573 | $56,727 |
| 3 | 573 | 57 | 17 | 613 | $60,687 |
| ... | ... | ... | ... | ... | ... |
| 12 | 1,105 | 111 | 33 | 1,183 | $117,117 |

### Formula
New Customers = Previous Ending × Growth Rate
Churned = Starting × Churn Rate
Ending = Starting + New - Churned
MRR = Ending × ARPU
```

### Top-Down Model

```markdown
## Market Sizing (TAM/SAM/SOM)

### TAM (Total Addressable Market)
All potential customers if you had 100% market share
= Total businesses in category × Average deal size
= 10,000,000 × $1,000 = $10B

### SAM (Serviceable Addressable Market)
Customers you could realistically reach
= TAM × % in your target segment
= $10B × 5% = $500M

### SOM (Serviceable Obtainable Market)
Realistic near-term capture (1-3 years)
= SAM × Expected market share
= $500M × 2% = $10M
```

## Startup Financial Model

### P&L Template

```markdown
## Income Statement - [Year]

### Revenue
| Line Item | Q1 | Q2 | Q3 | Q4 | Total |
|-----------|----|----|----|----|-------|
| MRR | $30K | $45K | $65K | $90K | - |
| Services | $5K | $8K | $10K | $12K | - |
| **Total Revenue** | $95K | $143K | $205K | $282K | $725K |

### Cost of Goods Sold
| Line Item | Q1 | Q2 | Q3 | Q4 | Total |
|-----------|----|----|----|----|-------|
| Hosting | $3K | $4K | $6K | $8K | $21K |
| Support | $5K | $7K | $10K | $14K | $36K |
| **Total COGS** | $8K | $11K | $16K | $22K | $57K |

**Gross Profit**: $668K
**Gross Margin**: 92%

### Operating Expenses
| Line Item | Q1 | Q2 | Q3 | Q4 | Total |
|-----------|----|----|----|----|-------|
| Salaries | $60K | $80K | $100K | $120K | $360K |
| Marketing | $15K | $25K | $35K | $50K | $125K |
| G&A | $5K | $6K | $7K | $8K | $26K |
| **Total OpEx** | $80K | $111K | $142K | $178K | $511K |

**Operating Income**: $157K
**Operating Margin**: 22%
```

### Cash Flow Projection

```markdown
## Cash Flow - 12 Month

| Month | Revenue | Expenses | Net | Balance |
|-------|---------|----------|-----|---------|
| 1 | $30K | $50K | -$20K | $480K |
| 2 | $35K | $52K | -$17K | $463K |
| 3 | $40K | $55K | -$15K | $448K |
| ... | ... | ... | ... | ... |
| 12 | $120K | $95K | +$25K | $385K |

### Key Questions
- Runway: How many months until cash = 0?
- Break-even: When does Net > 0?
- Funding need: How much to reach profitability?
```

## Fundraising Models

### Cap Table

```markdown
## Capitalization Table

### Pre-Money (Before Investment)

| Shareholder | Shares | % Ownership |
|-------------|--------|-------------|
| Founder A | 4,000,000 | 40% |
| Founder B | 4,000,000 | 40% |
| Option Pool | 2,000,000 | 20% |
| **Total** | 10,000,000 | 100% |

### Post-Money (After $2M at $8M Pre)

| Shareholder | Shares | % Ownership |
|-------------|--------|-------------|
| Founder A | 4,000,000 | 32% |
| Founder B | 4,000,000 | 32% |
| Option Pool | 2,000,000 | 16% |
| Series A | 2,500,000 | 20% |
| **Total** | 12,500,000 | 100% |

New shares = Investment / Price per share
Price per share = Pre-money valuation / Pre-money shares
= $8M / 10M = $0.80
New shares = $2M / $0.80 = 2,500,000
```

### Use of Funds

```markdown
## Use of Funds - $2M Raise

| Category | Amount | % | Duration |
|----------|--------|---|----------|
| Engineering (4 hires) | $800K | 40% | 18 months |
| Sales & Marketing | $600K | 30% | 18 months |
| Operations | $300K | 15% | 18 months |
| Buffer | $300K | 15% | - |
| **Total** | $2M | 100% | 18 mo runway |

### Milestones to Hit
- [ ] $100K MRR (from $30K)
- [ ] 500 customers (from 150)
- [ ] 10 enterprise deals
- [ ] Series A ready metrics
```

## Financial Formulas Reference

### Profitability
```
Gross Profit = Revenue - COGS
Gross Margin = Gross Profit / Revenue

Operating Income = Gross Profit - Operating Expenses
Operating Margin = Operating Income / Revenue

Net Income = Operating Income - Interest - Taxes
Net Margin = Net Income / Revenue
```

### SaaS Specific
```
MRR = Sum of all monthly subscriptions
ARR = MRR × 12
ACV = Total contract value / Contract years
ARPU = MRR / Total customers

Churn Rate = Customers lost / Starting customers
NRR = (Start MRR + Expansion - Churn) / Start MRR

Quick Ratio = (New MRR + Expansion) / (Churn + Contraction)
Target: > 4 (healthy growth)

CAC = Sales & Marketing spend / New customers
LTV = ARPU × Gross Margin × (1 / Churn rate)
LTV:CAC = Target > 3:1
Payback = CAC / (ARPU × Gross Margin)
```

### Valuation
```
Revenue Multiple = Valuation / ARR
Common SaaS multiples: 5-15x ARR

DCF = Σ (Cash Flow / (1 + r)^n)
Where r = discount rate, n = year

Rule of 40 = Growth Rate % + Profit Margin %
Target: > 40%
```

## Spreadsheet Tips

### Best Practices
- Separate inputs (blue), calculations (black), outputs (green)
- Use named ranges for key assumptions
- Build scenarios (base, bull, bear)
- Include a summary dashboard
- Document all assumptions
- Version control your models

### Common Errors to Avoid
- Circular references without iteration
- Hardcoded values in formulas
- Missing negative signs for expenses
- Inconsistent time periods
- Not stress-testing assumptions
