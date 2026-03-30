# Market Data Dependency Mapper Test Scenarios

## Purpose
Test whether Claude can comprehensively document market data feeds and dependencies for AI capabilities, identifying criticality, backup sources, and operational resilience considerations.

---

## Test Input: AI Capability Market Data Environment

### Capability: AI-Powered Portfolio Risk Analytics

**Description:**
```
AI system that provides real-time portfolio risk metrics including VaR,
stress scenarios, and factor exposures. Used by portfolio managers and
risk management for position monitoring and limit compliance.

Functionality:
- Calculate real-time Value at Risk across portfolios
- Run stress scenarios against current positions
- Decompose risk by factor exposures
- Alert on limit breaches
- Generate end-of-day risk reports

Asset Classes:
- Equities (US, International)
- Fixed Income (Government, Corporate, Municipal)
- Derivatives (Listed options, OTC swaps)
- FX

Users: Portfolio managers, Risk management, Trading desk, Compliance
```

**Market Data Feeds:**
```
Currently Using:
- Bloomberg (equities, fixed income pricing, FX rates)
- ICE (derivatives pricing, volatility surfaces)
- Refinitiv (backup pricing, economic data)
- Internal: Position feed from OMS
- Internal: Trade feed from execution system

Usage Pattern:
- Real-time streaming during market hours
- End-of-day batch for official NAV/risk
- Historical data for backtesting and model calibration
```

---

## What the Skill Should Produce

### 1. Data Feed Inventory
- Complete list of market data sources
- Data elements from each source
- Refresh frequencies and latencies

### 2. Criticality Assessment
- Critical vs. supplementary data
- Impact of unavailability
- Recovery time objectives

### 3. Dependency Mapping
- Which AI functions depend on which data
- Cascade effects of data failures
- Single points of failure

### 4. Backup and Failover
- Primary/secondary source mapping
- Failover procedures
- Data quality considerations when switching

### 5. Cost and Contract Summary
- Vendor relationships
- Contract terms relevant to operations
- Cost allocation considerations

---

## Pressure Points for Baseline Testing

### 1. Incomplete Feed Inventory
Agent may:
- List major vendors only
- Miss internal data dependencies

Should capture: All feeds including internal, reference data, derived data

### 2. No Criticality Differentiation
Agent may:
- Treat all feeds equally
- Not assess business impact of loss

Should classify: Critical (blocks operations) vs. important vs. supplementary

### 3. Missing Cascade Analysis
Agent may:
- Evaluate feeds independently
- Not show how failures cascade

Should map: "If X fails, then Y and Z also fail"

### 4. No Backup Source Mapping
Agent may:
- Document primary sources only
- Not identify alternatives

Should include: Backup for each critical feed, switching procedure

### 5. Latency/Timeliness Not Addressed
Agent may:
- Document data availability
- Not address timeliness requirements

Should specify: Required latency, actual latency, impact of delays

### 6. Contract Terms Missing
Agent may:
- Focus on technical aspects
- Ignore operational contract terms

Should include: SLAs, redistribution rights, usage restrictions

---

## Expected Output Quality

### Poor (Baseline Expected)
```
Market Data Dependencies for Portfolio Risk Analytics

Data Sources:
1. Bloomberg - equity and fixed income prices
2. ICE - derivatives pricing
3. Refinitiv - backup pricing
4. Internal OMS - positions
5. Internal execution - trades

The system requires real-time market data during trading hours
and end-of-day data for official calculations.

If data is unavailable, manual workarounds may be needed.
```

### Good (With Skill)
```yaml
market_data_dependency_map:
  capability: "AI-Powered Portfolio Risk Analytics"
  document_date: "2026-01-24"
  owner: "[Market Data Management]"
  review_frequency: "Quarterly"

data_feed_inventory:
  external_feeds:
    - feed_id: "MKT-001"
      vendor: "Bloomberg"
      feed_name: "Bloomberg B-PIPE"
      data_elements:
        - element: "Equity prices (real-time)"
          coverage: "US, EMEA, APAC exchanges"
          refresh: "Real-time streaming"
          latency: "<100ms from exchange"

        - element: "Fixed income prices"
          coverage: "Government, corporate, municipal"
          refresh: "Real-time (liquid), periodic (illiquid)"
          latency: "Real-time to 15-min for illiquid"

        - element: "FX rates"
          coverage: "Major and emerging pairs"
          refresh: "Real-time streaming"
          latency: "<50ms"

        - element: "Reference data"
          coverage: "Security master, corporate actions"
          refresh: "Daily batch + intraday updates"
          latency: "T+0 for corporate actions"

      contract:
        contract_id: "[Contract reference]"
        expiry: "2027-12-31"
        sla: "99.95% availability"
        redistribution: "Internal use only"
        usage_restrictions: "No derived data redistribution"
        cost_structure: "Per-terminal + enterprise data fee"
        annual_cost: "$XXX,XXX"

    - feed_id: "MKT-002"
      vendor: "ICE Data Services"
      feed_name: "ICE Derivatives Feed"
      data_elements:
        - element: "Options prices"
          coverage: "US listed options"
          refresh: "Real-time streaming"
          latency: "<100ms"

        - element: "Volatility surfaces"
          coverage: "Major indices, single stocks"
          refresh: "Real-time calculated"
          latency: "<500ms"

        - element: "OTC swap curves"
          coverage: "Interest rate, credit swaps"
          refresh: "15-minute snapshots"
          latency: "15 minutes"

      contract:
        contract_id: "[Contract reference]"
        expiry: "2026-06-30"
        sla: "99.9% availability"
        redistribution: "Limited internal use"
        annual_cost: "$XX,XXX"

    - feed_id: "MKT-003"
      vendor: "Refinitiv"
      feed_name: "Refinitiv Real-Time"
      data_elements:
        - element: "Equity prices (backup)"
          coverage: "Global exchanges"
          refresh: "Real-time streaming"
          latency: "<150ms"

        - element: "Economic indicators"
          coverage: "Global macro data"
          refresh: "Event-driven"
          latency: "Real-time on release"

      contract:
        contract_id: "[Contract reference]"
        expiry: "2027-03-31"
        sla: "99.9% availability"
        note: "Designated backup source"
        annual_cost: "$XX,XXX"

  internal_feeds:
    - feed_id: "INT-001"
      system: "Order Management System (OMS)"
      feed_name: "Position Feed"
      data_elements:
        - element: "Current positions"
          coverage: "All portfolios"
          refresh: "Real-time"
          latency: "<1 second from trade"

        - element: "Pending orders"
          coverage: "Open orders"
          refresh: "Real-time"
          latency: "<1 second"

      ownership:
        system_owner: "[Trading Technology]"
        data_owner: "[Operations]"
      sla: "99.99% during market hours"

    - feed_id: "INT-002"
      system: "Execution Management System"
      feed_name: "Trade Feed"
      data_elements:
        - element: "Executed trades"
          coverage: "All executions"
          refresh: "Real-time"
          latency: "<500ms from execution"

      ownership:
        system_owner: "[Trading Technology]"
        data_owner: "[Operations]"

    - feed_id: "INT-003"
      system: "Security Master"
      feed_name: "Reference Data Feed"
      data_elements:
        - element: "Security attributes"
          coverage: "All tradeable securities"
          refresh: "Daily + intraday"
          latency: "T+0 for new issues"

      ownership:
        system_owner: "[Data Management]"

criticality_assessment:
  critical_feeds:
    - feed_id: "MKT-001"
      vendor: "Bloomberg"
      criticality: "CRITICAL"
      rationale: |
        Primary source for equity and FI pricing.
        Risk calculations cannot run without pricing data.
        No single alternative covers full scope.
      impact_if_unavailable: |
        - Real-time risk monitoring stops
        - Limit monitoring delayed
        - EOD risk reports delayed
      rto: "15 minutes (failover to backup)"
      rpo: "0 (real-time data)"

    - feed_id: "INT-001"
      system: "OMS Position Feed"
      criticality: "CRITICAL"
      rationale: |
        Without positions, risk calculations are meaningless.
        No external alternative exists.
      impact_if_unavailable: |
        - All risk calculations stop
        - Cannot assess portfolio exposure
        - Limit monitoring impossible
      rto: "5 minutes (system redundancy)"
      rpo: "0"

  important_feeds:
    - feed_id: "MKT-002"
      vendor: "ICE"
      criticality: "IMPORTANT"
      rationale: |
        Required for derivatives risk.
        Partial backup available through Bloomberg.
      impact_if_unavailable: |
        - Derivatives risk degraded (less accurate)
        - Vol surface interpolation required
        - OTC swap risk estimated
      degraded_operation: "Use Bloomberg for listed; estimate OTC"

  supplementary_feeds:
    - feed_id: "MKT-003"
      vendor: "Refinitiv"
      criticality: "SUPPLEMENTARY"
      rationale: |
        Designated backup; economic data is enrichment.
      impact_if_unavailable: |
        - Backup unavailable (elevated risk)
        - Economic scenario analysis limited

function_dependency_mapping:
  function_1:
    function: "Real-time VaR Calculation"
    required_data:
      - feed: "MKT-001 (Bloomberg)"
        elements: ["Equity prices", "FI prices", "FX rates"]
        required: true
        fallback: "MKT-003 (Refinitiv)"

      - feed: "INT-001 (Positions)"
        elements: ["Current positions"]
        required: true
        fallback: "None - function stops"

      - feed: "MKT-002 (ICE)"
        elements: ["Vol surfaces"]
        required: "For options"
        fallback: "Bloomberg implied vol"

    failure_cascade: |
      If Bloomberg fails → Failover to Refinitiv (15 min delay)
      If OMS fails → VaR calculation stops entirely
      If ICE fails → Options risk degraded but continues

  function_2:
    function: "Stress Testing"
    required_data:
      - feed: "INT-001 (Positions)"
        required: true
      - feed: "Historical data (stored)"
        required: true
      - feed: "Real-time prices"
        required: false
        note: "Can run on last known prices"

    failure_cascade: |
      Less sensitive to real-time feed issues.
      Can run on T-1 positions if OMS delayed.

  function_3:
    function: "Limit Monitoring"
    required_data:
      - feed: "MKT-001 (Bloomberg)"
        required: true
      - feed: "INT-001 (Positions)"
        required: true

    failure_cascade: |
      Both required for limit monitoring.
      If either fails, manual limit checks required.

cascade_analysis:
  single_points_of_failure:
    - spof: "OMS Position Feed"
      impact: "All risk functions stop"
      mitigation: "OMS has redundant architecture"
      residual_risk: "LOW"

    - spof: "Security Master"
      impact: "New securities not priced correctly"
      mitigation: "Manual security setup as backup"
      residual_risk: "LOW"

  cascade_scenarios:
    - scenario: "Bloomberg outage"
      affected_functions: ["Real-time VaR", "Limit monitoring"]
      cascade_effect: |
        1. Pricing stops for equities, FI, FX
        2. VaR calculation uses stale prices (degraded)
        3. Limit monitoring alerts on stale data
        4. After 15 min, failover to Refinitiv
      mitigation: "Automated failover to Refinitiv"
      residual_impact: "15 minutes degraded; then recovered"

    - scenario: "OMS outage"
      affected_functions: ["ALL risk functions"]
      cascade_effect: |
        1. Position feed stops
        2. All risk calculations stop
        3. Trading can continue but blind to risk
      mitigation: "OMS redundancy; manual position backup"
      residual_impact: "HIGH if OMS redundancy fails"

backup_and_failover:
  primary_backup_mapping:
    - data_category: "Equity Prices"
      primary: "Bloomberg (MKT-001)"
      backup: "Refinitiv (MKT-003)"
      failover_trigger: "Bloomberg feed delay >5 min OR explicit outage"
      failover_procedure: "Automated switch in feed handler"
      data_quality_delta: "Latency increases ~50ms; coverage equivalent"
      tested: "2025-Q3 (successful)"

    - data_category: "Fixed Income Prices"
      primary: "Bloomberg (MKT-001)"
      backup: "Refinitiv (MKT-003)"
      failover_trigger: "Same as equity"
      data_quality_delta: "Illiquid bond coverage may differ"
      tested: "2025-Q3"

    - data_category: "Derivatives/Vol"
      primary: "ICE (MKT-002)"
      backup: "Bloomberg (partial)"
      failover_trigger: "ICE feed delay >10 min"
      data_quality_delta: "Vol surface less granular; OTC estimated"
      tested: "2025-Q2"

    - data_category: "Positions"
      primary: "OMS (INT-001)"
      backup: "None (system redundancy)"
      failover_trigger: "N/A"
      data_quality_delta: "N/A"
      note: "OMS has built-in HA; no external backup possible"

  failover_testing:
    schedule: "Quarterly"
    last_test: "2025-Q3"
    next_test: "2026-Q1"
    results_location: "[DR Test Report]"

operational_considerations:
  market_hours_requirements:
    - period: "US Market Hours (09:30-16:00 ET)"
      requirement: "Real-time pricing required"
      latency_tolerance: "<500ms for risk calc refresh"
      degraded_mode: "Stale prices acceptable for 15 min max"

    - period: "Extended Hours (04:00-09:30, 16:00-20:00 ET)"
      requirement: "Best efforts real-time"
      latency_tolerance: "<2 seconds acceptable"
      degraded_mode: "Close prices acceptable"

    - period: "Overnight"
      requirement: "EOD prices sufficient"
      latency_tolerance: "N/A"

  vendor_contact_information:
    - vendor: "Bloomberg"
      support: "[Support contact]"
      escalation: "[Account manager]"
      outage_notification: "Via Bloomberg terminal + email"

    - vendor: "ICE"
      support: "[Support contact]"
      escalation: "[Account manager]"

  monitoring_and_alerting:
    - monitor: "Feed latency"
      threshold: ">5 seconds"
      alert: "Operations + Risk"

    - monitor: "Data staleness"
      threshold: ">15 minutes during market hours"
      alert: "Operations + Risk + Trading"

    - monitor: "Coverage gaps"
      threshold: ">1% securities unpriced"
      alert: "Data Management"

cost_summary:
  annual_costs:
    - vendor: "Bloomberg"
      cost: "$XXX,XXX"
      allocation: "Shared across trading, risk, research"

    - vendor: "ICE"
      cost: "$XX,XXX"
      allocation: "Risk + Trading"

    - vendor: "Refinitiv"
      cost: "$XX,XXX"
      allocation: "Backup/DR"

  total_annual: "$XXX,XXX"
  cost_per_function: "Risk analytics ~40% of total"

review_and_maintenance:
  document_owner: "[Market Data Management]"
  review_frequency: "Quarterly"
  last_review: "2026-01-24"
  next_review: "2026-04-24"
  change_triggers:
    - "New data feed added"
    - "Vendor contract change"
    - "New AI function deployed"
    - "Failover test results"
```

---

## Financial Services Context

Market data dependency mapping for financial services AI requires:

- **Criticality classification:** Not all data is equally important
- **Cascade analysis:** Understand how failures propagate
- **Failover documentation:** Know the backup and how to switch
- **Latency awareness:** Real-time requirements vary by function
- **Contract awareness:** Redistribution rights, SLAs, costs
- **Testing evidence:** Failover must be tested, not assumed
