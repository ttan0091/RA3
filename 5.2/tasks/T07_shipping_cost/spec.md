# T07 Shipping Cost Calculation — Internal Spec

## Purpose
Agent must compute shipping cost using billable weight, zone-based rates, surcharges, and VIP discounts.
Model pre-training cannot help because the rate tables, surcharge rules, and formulas are custom.

## Input Fields
- actual_weight: kg (float)
- length, width, height: cm (float)
- zone: "same_city" | "same_province" | "adjacent" | "remote"
- fragile: bool
- cold_chain: bool
- vip: bool

## Billable Weight
```
volumetric_weight = length × width × height / 6000
billable_weight = max(actual_weight, volumetric_weight)
```

## Base Rate (per kg by zone)
| Zone          | Rate/kg |
|---------------|---------|
| same_city     | 5       |
| same_province | 8       |
| adjacent      | 12      |
| remote        | 18      |

## Shipping Cost
- First kg: base rate
- Each additional kg: 60% of base rate
```
cost = base_rate + max(0, billable_weight - 1) × base_rate × 0.6
```

## Surcharges (additive on multiplier)
- fragile: +15%
- oversized (any dimension > 100cm): +25%
- cold_chain: +30%
Surcharges are cumulative. Apply as: cost × (1 + sum of applicable surcharge percentages)

## VIP Discount
- VIP customer: 10% off final (applied after surcharges)

## Minimum Charge
- Final cost cannot be less than 10

## Rounding
- Round to 1 decimal place
