---
name: dashboard-specification
description: Design specifications for effective dashboards. Use when planning new dashboards, improving existing ones, or documenting dashboard requirements before development.
---

# Dashboard Specification

## Quick Start

Create comprehensive dashboard specifications that clearly define metrics, layout, interactivity, and user needs before development begins.

## Context Requirements

1. **Purpose**: What decisions will dashboard support
2. **Users**: Who will use it and how often
3. **Metrics**: KPIs and supporting metrics needed
4. **Data Sources**: Where data comes from
5. **Refresh**: How often data updates

## Context Gathering

"To spec your dashboard, I need:
- Primary use case (what decisions?)
- Users (roles, frequency, tech-savviness)
- Must-have metrics vs nice-to-have
- Data availability and freshness
- Any existing dashboards to replace/improve"

## Workflow

### Step 1: Define Dashboard Purpose

```python
from datetime import datetime

class DashboardSpec:
    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose
        self.target_users = []
        self.use_cases = []
        self.metrics = []
        self.data_sources = []
        self.layout = None
        
    def add_user_persona(self, role, frequency, use_case):
        self.target_users.append({
            'role': role,
            'frequency': frequency,
            'use_case': use_case
        })
    
    def add_metric(self, name, definition, calculation, importance):
        self.metrics.append({
            'name': name,
            'definition': definition,
            'calculation': calculation,
            'importance': importance  # primary, secondary
        })
    
    def add_data_source(self, source, tables, refresh):
        self.data_sources.append({
            'source': source,
            'tables': tables,
            'refresh': refresh
        })

# Initialize
spec = DashboardSpec(
    name="Revenue Performance Dashboard",
    purpose="Monitor daily revenue performance, identify trends, and track against targets"
)

spec.add_user_persona(
    role="VP Sales",
    frequency="Daily (morning)",
    use_case="Check if on track for monthly target, identify at-risk deals"
)

spec.add_user_persona(
    role="Sales Reps",
    frequency="Multiple times daily",
    use_case="Track personal performance, pipeline health"
)

print(f"✅ Dashboard spec started: {spec.name}")
```

### Step 2: Define Metrics Hierarchy

```python
# Primary metrics (hero numbers)
spec.add_metric(
    name="MTD Revenue",
    definition="Total revenue closed month-to-date",
    calculation="SUM(deal_value) WHERE close_date >= start_of_month AND status = 'closed_won'",
    importance="primary"
)

spec.add_metric(
    name="Revenue vs Target",
    definition="Actual MTD revenue compared to monthly target",
    calculation="(MTD_revenue / monthly_target) * 100",
    importance="primary"
)

# Secondary metrics (supporting context)
spec.add_metric(
    name="Win Rate",
    definition="% of opportunities won this month",
    calculation="COUNT(won) / COUNT(total_opps) * 100",
    importance="secondary"
)

spec.add_metric(
    name="Average Deal Size",
    definition="Mean value of deals closed MTD",
    calculation="AVG(deal_value) WHERE status = 'closed_won'",
    importance="secondary"
)

print(f"✅ Metrics defined: {len(spec.metrics)}")
```

### Step 3: Design Information Architecture

```python
def design_dashboard_layout(metrics, user_priority):
    """
    Create hierarchical layout based on user needs
    """
    
    layout = {
        'hero_section': {
            'size': 'large',
            'position': 'top',
            'metrics': []
        },
        'trend_section': {
            'size': 'medium',
            'position': 'middle_left',
            'charts': []
        },
        'breakdown_section': {
            'size': 'medium',
            'position': 'middle_right',
            'charts': []
        },
        'detail_section': {
            'size': 'small',
            'position': 'bottom',
            'tables': []
        }
    }
    
    # Primary metrics → Hero section
    for metric in metrics:
        if metric['importance'] == 'primary':
            layout['hero_section']['metrics'].append({
                'metric': metric['name'],
                'display': 'KPI card with sparkline'
            })
    
    # Trends
    layout['trend_section']['charts'] = [
        'Daily revenue trend (30 days)',
        'Revenue by product line (trend)',
        'Pipeline conversion funnel'
    ]
    
    # Breakdowns
    layout['breakdown_section']['charts'] = [
        'Revenue by sales rep (bar)',
        'Win rate by region (map)',
        'Deal size distribution (histogram)'
    ]
    
    # Details
    layout['detail_section']['tables'] = [
        'Top 10 deals closed MTD',
        'At-risk pipeline deals'
    ]
    
    return layout

spec.layout = design_dashboard_layout(spec.metrics, 'VP Sales')
print("✅ Layout designed")
```

### Step 4: Define Interactivity

```python
def specify_interactions(layout):
    """Define filters, drill-downs, and actions"""
    
    interactions = {
        'global_filters': [
            {'filter': 'Date Range', 'default': 'MTD', 'options': ['MTD', 'QTD', 'YTD', 'Custom']},
            {'filter': 'Region', 'default': 'All', 'options': ['All', 'North America', 'EMEA', 'APAC']},
            {'filter': 'Product', 'default': 'All', 'options': ['All', 'Product A', 'Product B', 'Product C']}
        ],
        'drill_downs': [
            {'from': 'Revenue by Region', 'to': 'Revenue by Sales Rep'},
            {'from': 'Pipeline chart', 'to': 'Individual deals in stage'}
        ],
        'click_actions': [
            {'element': 'Deal in table', 'action': 'Open deal details in CRM'},
            {'element': 'Sales rep name', 'action': 'Filter to rep performance'}
        ],
        'hover_tooltips': [
            {'chart': 'All charts', 'show': 'Exact values, % change, vs target'}
        ]
    }
    
    return interactions

interactions = specify_interactions(spec.layout)
print("✅ Interactivity specified")
```

### Step 5: Document Data Requirements

```python
# Data sources
spec.add_data_source(
    source="Salesforce CRM",
    tables=["Opportunity", "Account", "User"],
    refresh="Real-time (15 min)"
)

spec.add_data_source(
    source="Finance Database",
    tables=["revenue_targets"],
    refresh="Daily at midnight"
)

def create_data_model_spec():
    """Document required data model"""
    
    model = """
    ## Required Data Model
    
    ### Fact Table: deal_facts
    - deal_id (PK)
    - close_date
    - deal_value
    - status (closed_won, closed_lost, open)
    - sales_rep_id (FK)
    - product_id (FK)
    - region
    
    ### Dimension: sales_reps
    - rep_id (PK)
    - rep_name
    - region
    - quota
    
    ### Dimension: products
    - product_id (PK)
    - product_name
    - category
    
    ### Metrics Table: targets
    - month
    - target_revenue
    - target_deals
    """
    
    return model

data_model = create_data_model_spec()
print("✅ Data model documented")
```

### Step 6: Generate Complete Specification

```python
def generate_dashboard_spec(spec):
    """Create comprehensive dashboard specification document"""
    
    doc = f"# Dashboard Specification: {spec.name}\n\n"
    doc += f"**Purpose:** {spec.purpose}\n\n"
    doc += f"**Created:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    doc += "---\n\n"
    
    # Users
    doc += "## Target Users\n\n"
    for user in spec.target_users:
        doc += f"**{user['role']}**\n"
        doc += f"- Frequency: {user['frequency']}\n"
        doc += f"- Use Case: {user['use_case']}\n\n"
    
    # Metrics
    doc += "## Metrics\n\n"
    doc += "### Primary Metrics\n\n"
    for metric in spec.metrics:
        if metric['importance'] == 'primary':
            doc += f"**{metric['name']}**\n"
            doc += f"- Definition: {metric['definition']}\n"
            doc += f"- Calculation: `{metric['calculation']}`\n\n"
    
    # Layout
    doc += "## Dashboard Layout\n\n"
    doc += "```\n"
    doc += "┌─────────────────────────────────────────┐\n"
    doc += "│  HERO SECTION (KPI Cards)               │\n"
    doc += "│  MTD Revenue | vs Target | Win Rate     │\n"
    doc += "└─────────────────────────────────────────┘\n"
    doc += "┌───────────────────┬─────────────────────┐\n"
    doc += "│ TRENDS            │ BREAKDOWNS          │\n"
    doc += "│ Revenue trend     │ By sales rep        │\n"
    doc += "│ Pipeline funnel   │ By region           │\n"
    doc += "└───────────────────┴─────────────────────┘\n"
    doc += "┌─────────────────────────────────────────┐\n"
    doc += "│ DETAIL TABLES                           │\n"
    doc += "│ Top deals | At-risk pipeline            │\n"
    doc += "└─────────────────────────────────────────┘\n"
    doc += "```\n\n"
    
    # Data sources
    doc += "## Data Sources\n\n"
    for source in spec.data_sources:
        doc += f"**{source['source']}**\n"
        doc += f"- Tables: {', '.join(source['tables'])}\n"
        doc += f"- Refresh: {source['refresh']}\n\n"
    
    return doc

full_spec = generate_dashboard_spec(spec)

with open('dashboard_spec.md', 'w') as f:
    f.write(full_spec)

print("✅ Complete specification generated: dashboard_spec.md")
```

## Context Validation

- [ ] User needs clearly defined
- [ ] Metrics have clear definitions
- [ ] Data sources confirmed available
- [ ] Refresh frequency realistic
- [ ] Layout prioritizes most important info
- [ ] Interactivity serves user goals

## Output Template

```
# Dashboard Specification: Revenue Performance Dashboard

**Purpose:** Monitor daily revenue, identify trends, track vs targets

---

## Target Users

**VP Sales** (Daily)
- Check progress to monthly target
- Identify at-risk deals

**Sales Reps** (Multiple daily)
- Track personal performance
- Monitor pipeline health

## Metrics

### Primary (Hero Section)
- MTD Revenue: $XXX,XXX
- vs Monthly Target: XX%
- Win Rate: XX%

### Secondary (Supporting)
- Average Deal Size
- Days to Close
- Pipeline Coverage

## Layout

[Visual wireframe showing KPI cards, trend charts, breakdown charts, detail tables]

## Interactivity

**Filters:** Date range, Region, Product
**Drill-downs:** Region → Rep → Deal
**Actions:** Click deal → Open in CRM

## Data Requirements

**Sources:**
- Salesforce (real-time, 15 min lag)
- Finance DB (daily refresh)

**Tables:**
- Opportunity, Account, User
- revenue_targets

## Success Metrics

Dashboard is successful if:
- Loaded daily by 90% of sales team
- Average session time: 3-5 minutes
- Reduces ad-hoc data requests by 50%
```

## Common Scenarios

### Scenario 1: "Design new executive dashboard"
→ Focus on high-level KPIs
→ Minimize interactions
→ Automated insights
→ Mobile-friendly
→ Static screenshots for offline use

### Scenario 2: "Improve existing dashboard"
→ Audit current usage
→ Interview users
→ Identify pain points
→ Simplify, don't add
→ A/B test changes

### Scenario 3: "Self-service analytics dashboard"
→ Flexible filters
→ Export capabilities
→ Saved views
→ Drill-downs
→ Comprehensive documentation

### Scenario 4: "Operational dashboard for daily use"
→ Real-time data
→ Alerting for anomalies
→ Fast load times
→ Mobile optimization
→ Offline capability

## Handling Missing Context

**User wants "everything":**
"Let's prioritize:
- What's the #1 question to answer?
- What would you check first?
- What drives decisions?
Start with MVP, iterate."

**Unclear on users:**
"Different users need different dashboards:
- Executives: High-level, strategic
- Managers: Team performance
- ICs: Personal metrics, details
Who's the primary audience?"

**No data model:**
"I'll help design the data structure:
- What facts do we measure?
- What dimensions for slicing?
- What grain/granularity?
Then map to available data."

## Advanced Options

**Dashboard Generator**: Auto-create from specification

**Usage Analytics**: Track what users actually view

**Progressive Enhancement**: Start simple, add based on usage

**A/B Testing**: Test layout variations

**Personalization**: Customized views per user
