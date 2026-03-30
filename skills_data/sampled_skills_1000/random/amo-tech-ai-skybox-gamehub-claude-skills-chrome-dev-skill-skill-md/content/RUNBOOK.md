# Chrome DevTools MCP - Runbook

**Setup, usage, and troubleshooting guide for Chrome DevTools automation**

---

## Quick Setup

### 1. Install Chrome DevTools MCP

```bash
# Global installation
npm install -g chrome-devtools-mcp@latest

# Or use npx (no install needed)
npx chrome-devtools-mcp@latest
```

**Requirements:**
- Node.js 22+
- Chrome browser (latest version)

---

### 2. Configure Claude Code

Add to Claude Code MCP settings:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]
    }
  }
}
```

**Location:**
- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/claude-code/mcp_settings.json`

---

### 3. Verify Installation

```bash
# Check version
npx chrome-devtools-mcp@latest --version

# Test connection (opens Chrome)
npx chrome-devtools-mcp@latest
```

You should see:
```
Chrome DevTools MCP Server starting...
Browser opened successfully
MCP server listening
```

---

## Usage Examples

### Example 1: Smoke Test (1 minute)

**Input:**
```json
{
  "url": "http://localhost:8080",
  "action": "navigate"
}
```

**Then:**
```json
{ "url": "", "action": "console" }
{ "url": "", "action": "network" }
{ "url": "", "action": "screenshot", "options": { "filename": "smoke.png" } }
```

**Output:**
```json
{
  "result": "Console: 0 errors, Network: 12 requests succeeded",
  "artifacts": ["smoke.png"]
}
```

---

### Example 2: Performance Analysis (5 minutes)

**Input:**
```json
{
  "url": "http://localhost:8080/dashboard",
  "action": "performance"
}
```

**Output:**
```json
{
  "result": "Performance trace complete",
  "data": {
    "insights": {
      "LCPBreakdown": "LCP at 2.1s caused by slow image load",
      "CLSCulprits": "2 layout shifts from dynamic content",
      "DocumentLatency": "Document interactive at 1.5s",
      "RenderBlocking": "1 CSS file blocking render"
    }
  }
}
```

**Interpretation:**
- **LCP 2.1s** → Optimize images (use WebP, lazy loading)
- **CLS issues** → Reserve space for dynamic content
- **Render blocking** → Inline critical CSS or defer non-critical

---

### Example 3: Network Debugging

**Input:**
```json
{
  "url": "http://localhost:8080/pitch-deck-wizard",
  "action": "navigate"
}
```

**Then check network:**
```json
{
  "url": "",
  "action": "network",
  "options": { "resourceTypes": ["fetch", "xhr"] }
}
```

**Output:**
```json
{
  "result": "Network: 8 requests, 1 failed",
  "data": {
    "failed": [
      {
        "url": "/functions/v1/chat",
        "status": 401,
        "method": "POST"
      }
    ]
  }
}
```

**Action:** Fix authentication - API key missing or expired

---

### Example 4: Form Interaction

**Step 1: Navigate**
```json
{
  "url": "http://localhost:8080/events/new",
  "action": "navigate"
}
```

**Step 2: Get snapshot (to find UIDs)**
```json
{ "url": "", "action": "snapshot" }
```

**Step 3: Fill form**
```json
{
  "url": "",
  "action": "fill",
  "options": {
    "uid": "input-title-123",
    "value": "Tech Summit 2025"
  }
}
```

**Step 4: Submit**
```json
{
  "url": "",
  "action": "click",
  "options": { "uid": "button-submit-456" }
}
```

---

## Playbook Execution

### Running a Playbook

```bash
# Smoke test
cat playbooks/smoke.txt | npx chrome-devtools-mcp@latest

# Auth flow
cat playbooks/auth.txt | npx chrome-devtools-mcp@latest

# Performance trace
cat playbooks/performance.txt | npx chrome-devtools-mcp@latest
```

---

## Safety & Best Practices

### 🔒 Safety Rules

1. **Always snapshot before interacting**
   - Prevents "element not found" errors
   - Ensures you have correct UIDs

2. **Check console after actions**
   - Catch JavaScript errors immediately
   - Verify no unintended side effects

3. **Monitor network for failures**
   - Detect API issues early
   - Identify auth problems

4. **Reset throttling after tests**
   - Don't leave browser in slow mode
   - Use `{ throttlingOption: "No emulation" }`

5. **Close browser when done**
   - Free up system resources
   - Prevent zombie Chrome processes

---

### ⚡ Performance Tips

**Speed up tests:**
```bash
# Use headless mode (if supported)
npx chrome-devtools-mcp@latest --headless

# Skip unnecessary screenshots
# Only screenshot on failures
```

**Reduce trace overhead:**
```typescript
// Only trace critical paths
// Use autoStop: true
performance_start_trace({ reload: true, autoStop: true })
```

**Parallel execution:**
```typescript
// Run independent checks in parallel
Promise.all([
  checkConsole(),
  checkNetwork(),
  takeScreenshot()
])
```

---

## Troubleshooting

### Issue 1: Chrome won't start

**Symptom:** `Error: Failed to launch Chrome`

**Solutions:**
```bash
# Check Chrome is installed
google-chrome --version  # Linux
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # Mac

# Kill existing Chrome instances
pkill -f chrome
pkill -f chromium

# Retry
npx chrome-devtools-mcp@latest
```

---

### Issue 2: Element not found

**Symptom:** `Error: Element with UID 'button-123' not found`

**Solutions:**
1. **Always take snapshot first:**
   ```json
   { "url": "", "action": "snapshot" }
   ```

2. **Check UID in snapshot output**
   - Look for correct element UID
   - UIDs change on page reload

3. **Wait for page load:**
   ```json
   { "url": "", "action": "navigate", "options": { "timeout": 10000 } }
   ```

---

### Issue 3: Performance trace failed

**Symptom:** `Error: Trace recording failed`

**Solutions:**
1. **Ensure page loaded:**
   ```typescript
   // Wait after navigation
   await chrome.navigate_page({ url: "..." });
   await chrome.wait_for({ time: 2000 });
   ```

2. **Use autoStop:**
   ```json
   {
     "action": "performance",
     "options": { "reload": true, "autoStop": true }
   }
   ```

3. **Check Chrome memory:**
   ```bash
   # Chrome needs ~500MB for tracing
   free -h  # Linux
   top  # Mac
   ```

---

### Issue 4: Network requests missing

**Symptom:** Expected requests not showing up

**Solutions:**
1. **Filter by resource type:**
   ```json
   {
     "action": "network",
     "options": { "resourceTypes": ["fetch", "xhr"] }
   }
   ```

2. **Check timing - request might not have completed:**
   ```typescript
   // Wait after action
   await chrome.click({ uid: "submit" });
   await chrome.wait_for({ time: 2000 });
   const requests = await chrome.list_network_requests();
   ```

3. **Verify request actually fired:**
   - Open Chrome DevTools manually
   - Check Network tab
   - Verify request is made

---

### Issue 5: Slow test execution

**Symptom:** Tests taking too long

**Solutions:**
1. **Check throttling is disabled:**
   ```json
   { "action": "emulate_network", "options": { "throttlingOption": "No emulation" } }
   { "action": "emulate_cpu", "options": { "throttlingRate": 1 } }
   ```

2. **Reduce wait times:**
   ```typescript
   // Don't wait longer than needed
   wait_for({ text: "Success", timeout: 5000 })  // Not 30000
   ```

3. **Skip unnecessary screenshots:**
   - Only screenshot failures
   - Don't screenshot every step

---

### Issue 6: Dialog blocking automation

**Symptom:** Test hangs on alert/confirm

**Solutions:**
```json
{
  "action": "handle_dialog",
  "options": { "action": "accept" }
}
```

Or dismiss:
```json
{
  "action": "handle_dialog",
  "options": { "action": "dismiss" }
}
```

---

## Command Reference

### Start MCP Server

```bash
# Standard mode
npx chrome-devtools-mcp@latest

# Connect to existing Chrome (port forwarding)
npx chrome-devtools-mcp@latest --browserUrl http://localhost:9222

# WebSocket endpoint
npx chrome-devtools-mcp@latest --wsEndpoint ws://127.0.0.1:9222/devtools/browser/

# Isolated mode (temporary profile, auto-cleanup)
npx chrome-devtools-mcp@latest --isolated
```

---

### Common Actions

```json
// Navigate
{ "url": "http://localhost:8080", "action": "navigate" }

// Snapshot
{ "url": "", "action": "snapshot" }

// Screenshot
{ "url": "", "action": "screenshot", "options": { "filename": "test.png" } }

// Click
{ "url": "", "action": "click", "options": { "uid": "button-123" } }

// Fill
{ "url": "", "action": "fill", "options": { "uid": "input-456", "value": "text" } }

// Console
{ "url": "", "action": "console" }

// Network
{ "url": "", "action": "network" }

// Performance
{ "url": "http://localhost:8080/page", "action": "performance" }
```

---

## Performance Insights Reference

### Available Insights

| Insight Name | Measures | Good Threshold | Action Items |
|--------------|----------|----------------|--------------|
| `LCPBreakdown` | Largest Contentful Paint | <2.5s | Optimize images, reduce server response time |
| `CLSCulprits` | Cumulative Layout Shift | <0.1 | Reserve space for dynamic content, use size attributes |
| `DocumentLatency` | Time to Interactive | <3.5s | Reduce JavaScript execution, defer non-critical JS |
| `RenderBlocking` | Blocking resources | 0 blocking | Inline critical CSS, defer non-critical CSS/JS |
| `SlowCSSSelector` | CSS performance | <50ms | Simplify selectors, reduce nesting |

### How to Use

```json
{
  "url": "http://localhost:8080/dashboard",
  "action": "performance",
  "options": {
    "insightName": "LCPBreakdown"
  }
}
```

**Get all insights** (omit insightName):
```json
{
  "url": "http://localhost:8080/dashboard",
  "action": "performance"
}
```

---

## Network Throttling Reference

```json
// Slow 3G (400 Kbps, 400ms latency)
{ "action": "emulate_network", "options": { "throttlingOption": "Slow 3G" } }

// Fast 3G (1.6 Mbps, 150ms latency)
{ "action": "emulate_network", "options": { "throttlingOption": "Fast 3G" } }

// Fast 4G (40 Mbps, 5ms latency)
{ "action": "emulate_network", "options": { "throttlingOption": "Fast 4G" } }

// Offline
{ "action": "emulate_network", "options": { "throttlingOption": "Offline" } }

// Reset
{ "action": "emulate_network", "options": { "throttlingOption": "No emulation" } }
```

---

## CPU Throttling Reference

```json
// 4x slowdown (simulate low-end mobile)
{ "action": "emulate_cpu", "options": { "throttlingRate": 4 } }

// 6x slowdown (simulate very slow device)
{ "action": "emulate_cpu", "options": { "throttlingRate": 6 } }

// Reset (no throttling)
{ "action": "emulate_cpu", "options": { "throttlingRate": 1 } }
```

**Range:** 1-20x (1 = no throttling, 20 = 20x slower)

---

## Support

**Documentation:**
- FEATURES.md - Complete feature reference
- SKILL.md - Skill instructions and patterns
- Playbooks - Ready-to-run examples

**Official Resources:**
- GitHub: https://github.com/ChromeDevTools/chrome-devtools-mcp
- Chrome Blog: https://developer.chrome.com/blog/chrome-devtools-mcp
- NPM: https://www.npmjs.com/package/chrome-devtools-mcp

**Version:** 0.8.1 (Public Preview)
**Status:** Actively developed, seeking feedback

---

**Last Updated:** 2025-10-19
