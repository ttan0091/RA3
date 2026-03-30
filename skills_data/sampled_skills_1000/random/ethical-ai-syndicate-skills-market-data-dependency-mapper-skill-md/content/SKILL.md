---
name: market-data-dependency-mapper
description: Use when documenting market data feeds and dependencies for AI capabilities in trading or risk systems. Use during system design or resilience review. Maps feeds to functions with criticality, failover, and operational considerations.
---

# Market Data Dependency Mapper

## Overview

Document market data feeds comprehensively, including criticality assessment, cascade effects, and failover procedures. The goal is operational resilience through understanding exactly what data matters and what happens when it fails.

**Core principle:** Know which data failures stop operations versus degrade them. Plan for both.

## Output Format

```yaml
market_data_dependency_map:
  capability: "[AI Capability Name]"
  document_date: "[Date]"
  owner: "[Market Data Management / Team]"
  review_frequency: "[Quarterly recommended]"

data_feed_inventory:
  external_feeds:
    - feed_id: "[Unique identifier]"
      vendor: "[Vendor name]"
      feed_name: "[Feed/product name]"
      data_elements:
        - element: "[Data type]"
          coverage: "[What's covered]"
          refresh: "[Frequency]"
          latency: "[Typical latency]"
      contract:
        contract_id: "[Reference]"
        expiry: "[Date]"
        sla: "[Uptime commitment]"
        redistribution: "[Usage rights]"
        usage_restrictions: "[Limitations]"
        annual_cost: "[Cost]"

  internal_feeds:
    - feed_id: "[Unique identifier]"
      system: "[Source system]"
      feed_name: "[Feed name]"
      data_elements:
        - element: "[Data type]"
          coverage: "[Coverage]"
          refresh: "[Frequency]"
          latency: "[Latency]"
      ownership:
        system_owner: "[Team]"
        data_owner: "[Team]"
      sla: "[Internal SLA]"

criticality_assessment:
  critical_feeds:
    - feed_id: "[ID]"
      vendor: "[Vendor]"
      criticality: "CRITICAL"
      rationale: "[Why critical]"
      impact_if_unavailable: "[What happens]"
      rto: "[Recovery time objective]"
      rpo: "[Recovery point objective]"

  important_feeds:
    - feed_id: "[ID]"
      criticality: "IMPORTANT"
      rationale: "[Why important]"
      impact_if_unavailable: "[Degraded operation description]"
      degraded_operation: "[How to operate without]"

  supplementary_feeds:
    - feed_id: "[ID]"
      criticality: "SUPPLEMENTARY"
      rationale: "[Why supplementary]"
      impact_if_unavailable: "[Limited impact description]"

function_dependency_mapping:
  function_N:
    function: "[Function name]"
    required_data:
      - feed: "[Feed ID and name]"
        elements: ["[Required elements]"]
        required: true|false|"For [condition]"
        fallback: "[Backup source or 'None']"
    failure_cascade: |
      [What happens when each feed fails]
      [Order of degradation]

cascade_analysis:
  single_points_of_failure:
    - spof: "[Single point]"
      impact: "[What it affects]"
      mitigation: "[How addressed]"
      residual_risk: "[HIGH | MEDIUM | LOW]"

  cascade_scenarios:
    - scenario: "[Failure scenario]"
      affected_functions: ["[List of functions]"]
      cascade_effect: |
        [Step by step what happens]
      mitigation: "[How to respond]"
      residual_impact: "[After mitigation]"

backup_and_failover:
  primary_backup_mapping:
    - data_category: "[Data type]"
      primary: "[Primary source]"
      backup: "[Backup source]"
      failover_trigger: "[When to switch]"
      failover_procedure: "[How to switch]"
      data_quality_delta: "[Difference in backup]"
      tested: "[Last test date]"

  failover_testing:
    schedule: "[Testing frequency]"
    last_test: "[Date]"
    next_test: "[Date]"
    results_location: "[Where results documented]"

operational_considerations:
  market_hours_requirements:
    - period: "[Time period]"
      requirement: "[What's needed]"
      latency_tolerance: "[Acceptable delay]"
      degraded_mode: "[What's acceptable if degraded]"

  vendor_contact_information:
    - vendor: "[Vendor]"
      support: "[Contact]"
      escalation: "[Escalation path]"
      outage_notification: "[How they notify]"

  monitoring_and_alerting:
    - monitor: "[What's monitored]"
      threshold: "[Alert threshold]"
      alert: "[Who's notified]"

cost_summary:
  annual_costs:
    - vendor: "[Vendor]"
      cost: "[Amount]"
      allocation: "[Who pays]"
  total_annual: "[Total]"

review_and_maintenance:
  document_owner: "[Owner]"
  review_frequency: "[Frequency]"
  last_review: "[Date]"
  next_review: "[Date]"
  change_triggers:
    - "[What triggers document update]"
```

## Criticality Classification

### Classification Framework

| Level | Definition | Characteristics |
|-------|------------|-----------------|
| CRITICAL | Operations cannot function | No fallback; immediate business impact; regulatory implications |
| IMPORTANT | Operations degraded significantly | Fallback exists but limited; material accuracy impact |
| SUPPLEMENTARY | Operations continue with minor impact | Enhances but not required; easy workarounds |

### Classification Questions

For each feed, ask:
1. Can the AI function run without this data? (No = Critical)
2. Is there a backup source? (No backup for critical = single point of failure)
3. What is the business impact of stale data? (High = Critical/Important)
4. Can humans work around the gap? (Easily = Supplementary)

## Feed Inventory Details

### External Feeds

Capture for each external market data feed:

| Attribute | Why It Matters |
|-----------|----------------|
| Vendor and feed name | Identification |
| Data elements | Know exactly what you get |
| Coverage | Understand scope and gaps |
| Refresh frequency | Timeliness |
| Latency | Real-time vs. delayed |
| SLA | What's guaranteed |
| Contract terms | Redistribution, restrictions |
| Cost | Allocation and budgeting |

### Internal Feeds

Internal data sources also need documentation:

| Attribute | Why It Matters |
|-----------|----------------|
| Source system | Traceability |
| Data elements | What's provided |
| Refresh and latency | Timeliness |
| System owner | Escalation path |
| Data owner | Accountability |
| Internal SLA | Expectations |

## Function Dependency Mapping

Map which data each AI function requires:

```yaml
function_dependency:
  function: "Real-time VaR Calculation"

  required_data:
    - feed: "Bloomberg Equity Prices"
      elements: ["Real-time prices", "Last close"]
      required: true
      usage: "Mark positions to market"
      fallback: "Refinitiv (automatic failover)"

    - feed: "OMS Position Feed"
      elements: ["Current positions"]
      required: true
      usage: "Portfolio holdings"
      fallback: "None - function stops"

    - feed: "ICE Vol Surface"
      elements: ["Implied volatility"]
      required: "For options positions"
      usage: "Option risk calculation"
      fallback: "Bloomberg implied vol (degraded)"

  degradation_order:
    1. "If Bloomberg fails: Switch to Refinitiv (~15 min)"
    2. "If OMS fails: VaR stops entirely"
    3. "If ICE fails: Options risk estimated, flagged"
```

## Cascade Analysis

Document how failures propagate:

### Single Points of Failure

Identify and address:

```yaml
single_point_of_failure:
  component: "OMS Position Feed"
  why_single_point: "No external alternative for position data"
  impact_if_fails: "All risk calculations stop"
  mitigation:
    - "OMS has redundant architecture"
    - "Manual position backup procedure"
  residual_risk: "LOW (mitigation tested)"
  last_tested: "2025-Q3"
```

### Cascade Scenarios

Document end-to-end failure scenarios:

```yaml
cascade_scenario:
  trigger: "Bloomberg complete outage"

  cascade:
    - minute_0: "Bloomberg feed stops"
    - minute_1: "Pricing engine detects staleness"
    - minute_2: "Alert to operations"
    - minute_5: "Automatic failover to Refinitiv initiated"
    - minute_15: "Failover complete; operations resume"

  affected_functions:
    - "Real-time risk (degraded 0-15 min)"
    - "Limit monitoring (degraded 0-15 min)"
    - "Trading analytics (degraded 0-15 min)"

  not_affected:
    - "Position management"
    - "Order execution"

  residual_impact: "15 minutes of degraded risk monitoring"
```

## Backup and Failover

### Primary/Backup Mapping

For each critical data category:

| Data | Primary | Backup | Switch Time | Quality Delta |
|------|---------|--------|-------------|---------------|
| Equity prices | Bloomberg | Refinitiv | 15 min | +50ms latency |
| FI prices | Bloomberg | Refinitiv | 15 min | Less illiquid coverage |
| Vol surfaces | ICE | Bloomberg | 30 min | Less granular |
| Positions | OMS | None | N/A | System redundancy only |

### Failover Procedures

Document how to switch:

```yaml
failover_procedure:
  data_category: "Equity Prices"
  primary: "Bloomberg B-PIPE"
  backup: "Refinitiv"

  automatic_failover:
    trigger: "Bloomberg feed delay >5 minutes"
    action: "Feed handler switches to Refinitiv"
    notification: "Alert to operations"
    manual_intervention: "None required"

  manual_failover:
    trigger: "Explicit decision by operations"
    procedure:
      1. "Verify Bloomberg is actually down"
      2. "Enable Refinitiv feed in config"
      3. "Verify Refinitiv data flowing"
      4. "Disable Bloomberg feed"
    rollback: "Reverse steps when Bloomberg restored"

  testing:
    frequency: "Quarterly"
    last_test: "2025-Q3"
    result: "Successful; failover in 12 minutes"
```

## Operational Considerations

### Market Hours Requirements

| Period | Requirement | Tolerance |
|--------|-------------|-----------|
| Core market hours | Real-time pricing | <500ms latency |
| Pre-market | Best efforts | <2 seconds |
| After hours | End-of-day acceptable | N/A |
| Overnight | Prior close acceptable | N/A |

### Monitoring Framework

```yaml
monitoring:
  feed_latency:
    metric: "Time since last update"
    warning: ">2 seconds"
    critical: ">5 seconds"
    alert: "Operations pager"

  data_staleness:
    metric: "Age of most recent price"
    warning: ">5 minutes during market hours"
    critical: ">15 minutes during market hours"
    alert: "Operations + Risk management"

  coverage_gaps:
    metric: "% securities without price"
    warning: ">0.5%"
    critical: ">1%"
    alert: "Data management"
```

## Common Mistakes

| Mistake | Why It's Wrong | Do This Instead |
|---------|----------------|-----------------|
| List vendors only | Doesn't show data elements | Document specific data provided |
| No criticality assessment | Can't prioritize resilience | Classify critical/important/supplementary |
| Ignore internal feeds | They can fail too | Include all data sources |
| Backup "exists" | May not be tested | Document and test failover |
| Point-in-time latency | Varies by condition | Document typical and degraded |
| No cascade analysis | Miss interdependencies | Map failure propagation |

## Red Flags in Your Documentation

If your map has these, it's incomplete:

- Vendors listed without data elements
- No criticality classification
- Critical feeds without backup plan
- Failover procedures not documented
- Failover not tested (or test not documented)
- No monitoring specified
- Internal feeds missing

## Financial Services Context

Market data dependency mapping for financial services AI requires:

### Regulatory Awareness
- Business continuity expectations
- Examination of data resilience
- Documentation requirements

### Real-Time Sensitivity
- Trading and risk need current data
- Latency requirements vary by function
- Degraded operation must be defined

### Cost Awareness
- Market data is expensive
- Backup may be underutilized cost
- Understand cost/resilience trade-off

### Testing Culture
- Failover must be tested, not assumed
- Document test results
- Regular testing schedule
