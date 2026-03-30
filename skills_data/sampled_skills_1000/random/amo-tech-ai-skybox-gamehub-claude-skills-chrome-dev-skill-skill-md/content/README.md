# Chrome DevTools Automation Skill

**Production-ready browser automation, debugging, and performance analysis using Chrome DevTools MCP**

<p align="center">
  <strong>Simple • Powerful • Fast</strong><br>
  Control Chrome, analyze performance, debug issues—all from Claude.
</p>

---

## 🚀 Quick Start (60 seconds)

```bash
# 1. Install Chrome DevTools MCP
npm install -g chrome-devtools-mcp@latest

# 2. Start dev server
pnpm dev

# 3. Trigger skill via Claude Code
User: "Test homepage with Chrome DevTools"
Claude: [Runs smoke test playbook]
```

**Result:** Homepage tested, console checked, network monitored, screenshot captured ✅

---

## 📋 What You Get

✅ **Browser Automation** - Navigate, click, fill, interact with any page

✅ **Performance Analysis** - Record traces, measure Core Web Vitals, get AI insights

✅ **Network Debugging** - Monitor API calls, inspect requests/responses, check failures

✅ **Console Monitoring** - Catch JavaScript errors, warnings, logs

✅ **Visual Evidence** - Screenshot pages and specific elements

✅ **Multi-tab Support** - Test complex workflows across tabs

✅ **Network Emulation** - Test on Slow 3G, Fast 4G, Offline

✅ **CPU Throttling** - Simulate low-end devices

---

## 🎯 Use Cases

### 1. Smoke Test (1 minute)

**What:** Quick health check - page loads, no errors

**Command:**
```
User: "Run smoke test on homepage"
```

**What happens:**
1. Navigate to http://localhost:8080
2. Check console for errors
3. Monitor network requests
4. Capture screenshot

**Output:** ✅ or ❌ with details

---

### 2. Performance Analysis (5 minutes)

**What:** Measure Core Web Vitals, get optimization tips

**Command:**
```
User: "Analyze performance of dashboard"
```

**What happens:**
1. Record performance trace
2. Navigate to /dashboard
3. Measure LCP, CLS, FID
4. Get AI-powered insights

**Output:**
```
Performance Insights:
- LCP: 2.1s (caused by slow image load)
  → Recommendation: Optimize images, use WebP
- CLS: 2 layout shifts (from dynamic content)
  → Recommendation: Reserve space for content
- Render blocking: 1 CSS file
  → Recommendation: Inline critical CSS
```

---

### 3. Network Debugging (3 minutes)

**What:** Check API calls, find failures

**Command:**
```
User: "Debug network requests for pitch deck wizard"
```

**What happens:**
1. Navigate to /pitch-deck-wizard
2. Monitor all fetch/XHR requests
3. Check for 4xx/5xx errors
4. Inspect specific API calls

**Output:**
```
Network: 8 requests, 1 failed
Failed: POST /functions/v1/chat → 401 Unauthorized
```

---

## 📁 Project Structure

```
.claude/skills/chrome-dev-skill/
├── SKILL.md              # Main skill instructions (YAML + body)
├── README.md             # This file
├── RUNBOOK.md            # Setup & troubleshooting
├── FEATURES.md           # Complete feature reference
├── skill-handler.ts      # TypeScript implementation
│
└── playbooks/            # Ready-to-run test scenarios
    ├── smoke.txt        # 1-min health check
    ├── auth.txt         # 3-min auth flow
    └── performance.txt  # 5-min performance analysis

.claude/agents/eventos-chrome-agent/
└── agent.config.json     # Agent configuration
```

---

## 🛠️ Installation

### Prerequisites

- Node.js 22+
- Chrome browser (latest)
- Dev server running on port 8080

### Setup

```bash
# 1. Install Chrome DevTools MCP
npm install -g chrome-devtools-mcp@latest

# 2. Verify installation
npx chrome-devtools-mcp@latest --version

# 3. Test connection
npx chrome-devtools-mcp@latest
# Should see: "MCP server listening"

# 4. Start dev server
cd /home/sk/medellin-spark
pnpm dev
```

---

## 📚 Available Tests

### 1. Smoke Test (1 min)

**Tests:**
- Homepage loads
- No console errors
- Network requests succeed

**Trigger:**
```
"Run smoke test"
"Check if homepage works"
"Test basic functionality"
```

**Playbook:** [playbooks/smoke.txt](playbooks/smoke.txt)

---

### 2. Auth Flow (3 min)

**Tests:**
- Login form works
- Redirect after login
- Protected routes accessible
- Session persists

**Trigger:**
```
"Test authentication"
"Check login flow"
"Verify auth works"
```

**Playbook:** [playbooks/auth.txt](playbooks/auth.txt)

---

### 3. Performance Trace (5 min)

**Tests:**
- Core Web Vitals (LCP, CLS, FID)
- Render-blocking resources
- Network performance
- Slow CSS selectors

**Trigger:**
```
"Analyze performance"
"Check Core Web Vitals"
"Profile dashboard load time"
```

**Playbook:** [playbooks/performance.txt](playbooks/performance.txt)

---

## 🎬 Example Output

### Smoke Test

```
🚀 Starting smoke test...

Step 1: Navigate to homepage
✅ Homepage loaded (524ms)

Step 2: Check console
✅ No console errors

Step 3: Check network
Network: 12 total, 3 API calls
✅ All API calls successful

Step 4: Screenshot
📸 Saved: smoke-test-homepage.png

✅ Smoke test passed!
```

---

### Performance Analysis

```
🔄 Starting performance trace...
✅ Page loaded - trace recording...
⏹️  Stopping trace...
✅ Trace complete

📊 Analyzing LCP (Largest Contentful Paint)...
LCP Insight: LCP at 2.1s caused by slow image load

📊 Analyzing CLS (Cumulative Layout Shift)...
CLS Insight: 2 layout shifts from dynamic content

📊 Analyzing Render Blocking...
Render Blocking: 1 CSS file blocking render

============================================================
✅ PERFORMANCE TRACE COMPLETE
============================================================

Key Findings:
  - LCP: 2.1s (caused by slow image load)
  - CLS: 2 layout shifts (from dynamic content)
  - Render Blocking: 1 CSS file

💡 Recommendations:
  1. Optimize images (use WebP, lazy loading)
  2. Reserve space for dynamic content
  3. Inline critical CSS or defer non-critical
```

---

## 🤖 Using the Agent

The `eventos-chrome-agent` provides autonomous test execution:

**Trigger phrases:**
- "test with chrome devtools"
- "analyze performance"
- "check core web vitals"
- "debug browser issues"
- "inspect network requests"

**Example:**

```
User: "Test pitch deck wizard with Chrome DevTools"

Agent:
1. Navigates to /pitch-deck-wizard
2. Takes snapshot of page
3. Checks console for errors
4. Monitors network requests
5. Captures screenshots
6. Reports findings
```

---

## 🏗️ Features Overview

### Core Features (Essential)

| Feature | Use Case | Example |
|---------|----------|---------|
| `navigate_page` | Go to URLs | Test homepage |
| `take_snapshot` | Get page structure | Find element UIDs |
| `click` | Click elements | Submit form |
| `fill` | Enter text | Fill login form |
| `take_screenshot` | Visual evidence | Capture error state |
| `list_console_messages` | Check JS errors | Find bugs |
| `list_network_requests` | Monitor API | Debug failures |

### Advanced Features

| Feature | Use Case | Example |
|---------|----------|---------|
| `performance_start_trace` | Profile performance | Measure Core Web Vitals |
| `performance_analyze_insight` | Get AI tips | Optimize LCP |
| `emulate_network` | Test slow connections | Slow 3G simulation |
| `emulate_cpu` | Test low-end devices | 4x CPU throttle |
| `get_network_request` | Inspect API | Check request payload |
| `evaluate_script` | Run custom JS | Extract data |

**Complete reference:** [FEATURES.md](FEATURES.md)

---

## 📊 Performance Benchmarks

| Test | Duration | Coverage |
|------|----------|----------|
| Smoke Test | 1 min | Basic health check |
| Auth Flow | 3 min | Login/logout/session |
| Performance Trace | 5 min | Core Web Vitals + AI insights |

**Target SLAs:**
- Smoke test pass rate: **100%** (must always pass)
- Performance analysis: **<5 min** per page
- Network debugging: **<2 min** to find issue

---

## 🐛 Troubleshooting

**Common issues and quick fixes:**

### Chrome won't start
```bash
pkill -f chrome
npx chrome-devtools-mcp@latest
```

### Element not found
```
1. Take snapshot first
2. Find correct UID
3. Ensure page loaded
```

### Performance trace failed
```
1. Use autoStop: true
2. Wait after navigation
3. Check Chrome memory
```

### Network requests missing
```
1. Filter by resourceTypes: ["fetch", "xhr"]
2. Wait after action
3. Verify request actually fired
```

**Complete guide:** [RUNBOOK.md](RUNBOOK.md)

---

## 📖 Learning Resources

**Start here:**
1. [README.md](README.md) - This overview
2. [SKILL.md](SKILL.md) - Core instructions and patterns
3. [playbooks/smoke.txt](playbooks/smoke.txt) - Simplest example

**Go deeper:**
4. [FEATURES.md](FEATURES.md) - Complete feature reference
5. [playbooks/performance.txt](playbooks/performance.txt) - Performance analysis
6. [RUNBOOK.md](RUNBOOK.md) - Setup and troubleshooting

---

## 🤝 Contributing

**Adding a test:**

1. Create playbook in `playbooks/my-test.txt`
2. Test locally: `cat playbooks/my-test.txt | npx chrome-devtools-mcp@latest`
3. Update README
4. Submit PR

---

## 🆚 Chrome DevTools MCP vs Playwright MCP

| Aspect | Chrome DevTools | Playwright |
|--------|-----------------|------------|
| **Performance** | ✅ Built-in traces + AI | ❌ No native tools |
| **Cross-browser** | Chrome only | Chrome, Firefox, Safari |
| **Network** | ✅ Deep inspection | ✅ Basic monitoring |
| **Best For** | Performance work, debugging | Cross-browser E2E tests |

**Recommendation:** Use Chrome DevTools for performance. Use Playwright for cross-browser testing.

---

## 📜 License

MIT - See project root for license details

---

## 🙋 Support

**Need help?**

1. Check [SKILL.md](SKILL.md) for usage patterns
2. Check [RUNBOOK.md](RUNBOOK.md) for troubleshooting
3. Review [FEATURES.md](FEATURES.md) for complete reference
4. Check [playbooks/](playbooks/) for examples

**Found a bug?**

1. Capture screenshots
2. Save console logs
3. Document steps to reproduce
4. File GitHub issue

---

## 📞 Official Resources

- **GitHub:** https://github.com/ChromeDevTools/chrome-devtools-mcp
- **Chrome Blog:** https://developer.chrome.com/blog/chrome-devtools-mcp
- **NPM:** https://www.npmjs.com/package/chrome-devtools-mcp

**Version:** 0.8.1 (Public Preview)

---

<p align="center">
  <strong>Built following Anthropic Claude Skills best practices</strong><br>
  <em>Simple, powerful, and fast browser automation</em>
</p>
