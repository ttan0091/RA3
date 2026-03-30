# Chrome DevTools MCP - Features Summary

**Complete reference for Chrome DevTools MCP automation, debugging, and performance analysis**

Last Updated: 2025-10-19

---

## Overview

Chrome DevTools MCP provides **26 tools in 6 categories** for browser automation, debugging, and performance analysis. It uses the Chrome DevTools Protocol (CDP) and Puppeteer for reliable automation.

**Installation:**
```bash
npx chrome-devtools-mcp@latest
```

**Requirements:** Node.js 22+, Chrome browser

---

## Feature Categories

### 1. Core Automation (Essential for 90% of tasks)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `navigate_page` | Navigate to URL and wait for load | Go to specific page | Navigate to `/pitch-deck-wizard` | Core |
| `click` | Click element by UID from snapshot | Click buttons, links | Click "Create Event" button | Core |
| `fill` | Fill input fields or select options | Form submission | Enter event title "Tech Summit 2025" | Core |
| `take_snapshot` | Get page element tree with UIDs | See page structure before interacting | Get all form fields on event creation page | Core |
| `take_screenshot` | Capture page or element as PNG/JPEG | Visual evidence, debugging | Screenshot of pitch deck slide preview | Core |
| `list_console_messages` | Get console logs, warnings, errors | Debug JavaScript issues | Check for errors after deck generation | Core |
| `list_network_requests` | Get all network activity | Monitor API calls | Verify event creation API succeeded | Core |

### 2. Advanced Debugging (Deep inspection)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `get_network_request` | Get specific request details by URL | Inspect API request/response | Check pitch deck generation API payload | Advanced |
| `evaluate_script` | Execute JavaScript in page context | Run custom logic, extract data | Get computed event metrics from dashboard | Advanced |
| `list_processes` | List all running Chrome processes | Monitor resource usage | Check if browser is consuming too much memory | Advanced |
| `kill_process` | Terminate specific process by PID | Clean up hung processes | Kill stuck render process | Advanced |

### 3. Performance Analysis (Measure & optimize)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `performance_start_trace` | Begin recording performance trace | Start performance profiling | Record trace for dashboard load | Advanced |
| `performance_stop_trace` | Stop trace and get results | End profiling session | Stop trace after event creation | Advanced |
| `performance_analyze_insight` | Get AI insights from trace | Understand performance bottlenecks | Analyze LCP/FID/CLS for pitch deck wizard | Advanced |

### 4. Network Emulation (Test conditions)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `emulate_network` | Simulate network throttling | Test slow connections | Test pitch deck on "Slow 3G" | Advanced |
| `emulate_cpu` | Simulate CPU throttling (1-20x) | Test low-end devices | Test event dashboard on 4x throttle | Advanced |

### 5. Page Management (Multi-tab workflows)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `list_pages` | Get all open browser tabs | See active pages | List all event detail tabs open | Core |
| `new_page` | Open new tab with URL | Multi-page testing | Open event export in new tab | Core |
| `close_page` | Close tab by index | Clean up after test | Close event preview tab | Core |
| `select_page` | Switch context to specific tab | Work with different pages | Switch to main dashboard tab | Core |

### 6. Form Interactions (Advanced input)

| Feature | Description | Example Use Case | EventOS Example | Level |
|---------|-------------|------------------|-----------------|-------|
| `fill_form` | Fill multiple fields at once | Complete entire form | Fill all event creation fields together | Advanced |
| `hover` | Hover over element | Trigger tooltips, menus | Hover over event card to see actions | Advanced |
| `drag` | Drag element to another | Reorder items | Drag slide to reorder in pitch deck | Advanced |
| `upload_file` | Upload file through input | Test file uploads | Upload event banner image | Advanced |
| `handle_dialog` | Accept/dismiss alerts/confirms | Handle popups | Accept "Delete event?" confirmation | Advanced |

---

## Core vs Advanced Quick Reference

### Core Features (Use daily, must-know)

**Navigation & Inspection:**
- `navigate_page` - Go to URLs
- `take_snapshot` - Get page structure
- `take_screenshot` - Visual capture

**Interaction:**
- `click` - Click elements
- `fill` - Enter text/select options

**Debugging:**
- `list_console_messages` - Check JS errors
- `list_network_requests` - Monitor API calls

**Multi-page:**
- `list_pages` - See tabs
- `new_page` - Open tab
- `close_page` - Close tab

### Advanced Features (Use as needed)

**Deep Debugging:**
- `get_network_request` - Inspect specific API
- `evaluate_script` - Run custom JS
- `list_processes` / `kill_process` - Process control

**Performance:**
- `performance_start_trace` - Begin profiling
- `performance_stop_trace` - End profiling
- `performance_analyze_insight` - Get AI insights

**Testing:**
- `emulate_network` - Throttle network
- `emulate_cpu` - Throttle CPU

**Advanced Forms:**
- `fill_form` - Multi-field fill
- `hover` / `drag` / `upload_file` - Complex interactions
- `handle_dialog` - Alert handling

---

## EventOS Use Case Examples

### 1. Smoke Test (Core features only)

```typescript
// Navigate to dashboard
await chrome.navigate_page({ url: "http://localhost:8080" });

// Get page structure
await chrome.take_snapshot();

// Check console
const errors = await chrome.list_console_messages();

// Check network
const requests = await chrome.list_network_requests();

// Screenshot
await chrome.take_screenshot({ filename: "dashboard.png" });
```

**Result:** Quick health check in 30 seconds

---

### 2. Pitch Deck Creation (Core + some advanced)

```typescript
// Navigate to wizard
await chrome.navigate_page({ url: "http://localhost:8080/pitch-deck-wizard" });

// Get chat input
const snapshot = await chrome.take_snapshot();

// Fill and send message
await chrome.fill({ uid: "input-123", value: "Create deck for AI startup" });
await chrome.click({ uid: "button-456" });

// Wait for AI response
await chrome.wait_for({ text: "Tell me more" });

// Check network for API call
const requests = await chrome.list_network_requests({
  resourceTypes: ["fetch", "xhr"]
});

const apiCall = await chrome.get_network_request({
  url: "/functions/v1/pitch-deck-assistant"
});

console.log("API response:", apiCall.response);
```

**Result:** Test full AI conversation flow with network inspection

---

### 3. Performance Analysis (Advanced features)

```typescript
// Start performance trace
await chrome.performance_start_trace({
  reload: true,  // Reload page and record
  autoStop: true // Auto-stop after load
});

// Navigate to dashboard
await chrome.navigate_page({ url: "http://localhost:8080/dashboard" });

// Stop trace
await chrome.performance_stop_trace();

// Get AI insights
const insights = await chrome.performance_analyze_insight({
  insightName: "LCPBreakdown"
});

console.log("LCP Insights:", insights);
```

**Result:** Measure Core Web Vitals and get AI-powered optimization suggestions

---

### 4. Network Throttling Test (Advanced)

```typescript
// Emulate slow 3G
await chrome.emulate_network({
  throttlingOption: "Slow 3G"
});

// Navigate to heavy page
await chrome.navigate_page({ url: "http://localhost:8080/presentations" });

// Check load time
const requests = await chrome.list_network_requests();
const pageLoad = requests.find(r => r.url.includes("/presentations"));

console.log(`Load time on Slow 3G: ${pageLoad.duration}ms`);

// Reset to no throttling
await chrome.emulate_network({
  throttlingOption: "No emulation"
});
```

**Result:** Test app performance on slow connections

---

## Performance Insights Available

When using `performance_analyze_insight`, you can get detailed analysis for:

| Insight Name | What It Measures | Example Output |
|--------------|------------------|----------------|
| `DocumentLatency` | Time to document interactive | "Document became interactive at 1.2s" |
| `LCPBreakdown` | Largest Contentful Paint details | "LCP at 2.1s caused by slow image load" |
| `CLSCulprits` | Cumulative Layout Shift issues | "3 layout shifts from dynamic content" |
| `RenderBlocking` | Blocking resources | "2 CSS files blocking render" |
| `SlowCSSSelector` | Inefficient selectors | "Complex selector took 120ms" |

**Usage:**
```typescript
const insight = await chrome.performance_analyze_insight({
  insightName: "LCPBreakdown"
});
```

---

## Network Throttling Options

Available in `emulate_network`:

| Option | Download | Upload | Latency | Use Case |
|--------|----------|--------|---------|----------|
| No emulation | Unlimited | Unlimited | 0ms | Normal testing |
| Offline | 0 kbps | 0 kbps | 0ms | Offline mode |
| Slow 3G | 400 kbps | 400 kbps | 400ms | Very slow mobile |
| Fast 3G | 1.6 Mbps | 750 kbps | 150ms | Average mobile |
| Slow 4G | 4 Mbps | 3 Mbps | 20ms | Low-end mobile |
| Fast 4G | 40 Mbps | 20 Mbps | 5ms | Good mobile |

---

## Best Practices

### 1. Always Start with Snapshot

```typescript
// ✅ Good
const snapshot = await chrome.take_snapshot();
// Find element UIDs in snapshot
await chrome.click({ uid: "button-123" });

// ❌ Bad - guessing UIDs
await chrome.click({ uid: "unknown" });
```

### 2. Check Console After Actions

```typescript
await chrome.click({ uid: "submit-btn" });

const errors = await chrome.list_console_messages();
if (errors.length > 0) {
  console.error("Errors after submit:", errors);
}
```

### 3. Use Performance Traces for Key Flows

```typescript
// Only trace critical user paths
await chrome.performance_start_trace({ reload: true });
// ... user journey ...
await chrome.performance_stop_trace();
```

### 4. Reset Emulation After Tests

```typescript
// Always reset throttling
await chrome.emulate_network({ throttlingOption: "No emulation" });
await chrome.emulate_cpu({ throttlingRate: 1 });
```

---

## Tool Comparison: Chrome DevTools MCP vs Playwright MCP

| Aspect | Chrome DevTools MCP | Playwright MCP |
|--------|---------------------|----------------|
| **Automation** | Puppeteer-based, Chrome only | Cross-browser (Chrome, Firefox, Safari) |
| **Performance** | ✅ Built-in traces + AI insights | ❌ No native performance tools |
| **Network** | ✅ Deep inspection, emulation | ✅ Basic monitoring |
| **Debugging** | ✅ Console, processes, CDP | ✅ Console, network |
| **Element Selection** | UID from snapshot | Accessible name + ref |
| **Best For** | Performance analysis, Chrome debugging | Cross-browser E2E testing |

**Recommendation:** Use Chrome DevTools MCP for performance work and deep debugging. Use Playwright MCP for cross-browser E2E tests.

---

## Resources

**Official:**
- GitHub: https://github.com/ChromeDevTools/chrome-devtools-mcp
- Chrome Blog: https://developer.chrome.com/blog/chrome-devtools-mcp
- NPM: https://www.npmjs.com/package/chrome-devtools-mcp

**Community:**
- LobeHub: https://lobehub.com/mcp/chromedevtools-chrome-devtools-mcp
- Awesome MCP Servers: https://mcpservers.org/servers/github-com-chromedevtools-chrome-devtools-mcp

**Version:** 0.8.1 (Public Preview)
**Status:** Actively developed, seeking community feedback
