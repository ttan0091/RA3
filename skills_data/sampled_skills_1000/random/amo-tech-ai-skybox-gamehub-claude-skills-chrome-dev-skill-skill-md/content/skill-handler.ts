/**
 * Chrome DevTools MCP Skill Handler
 *
 * Executes browser automation, debugging, and performance analysis
 * using Chrome DevTools Protocol via MCP.
 */

export interface SkillInput {
  url: string;
  action: 'navigate' | 'snapshot' | 'screenshot' | 'click' | 'fill' | 'console' | 'network' | 'performance';
  options?: {
    uid?: string;              // Element UID for click/fill
    value?: string;            // Value for fill
    filename?: string;         // Screenshot filename
    fullPage?: boolean;        // Full page screenshot
    resourceTypes?: string[];  // Network request types
    insightName?: string;      // Performance insight name
    throttling?: string;       // Network throttling option
    [key: string]: any;
  };
}

export interface SkillOutput {
  result: string;
  artifacts?: string[];
  data?: {
    errors?: any[];
    requests?: any[];
    insights?: any;
    [key: string]: any;
  };
}

/**
 * Execute Chrome DevTools skill action
 */
export async function executeSkill(
  input: SkillInput,
  chrome: ChromeDevToolsMCP
): Promise<SkillOutput> {
  const { url, action, options = {} } = input;

  try {
    switch (action) {
      case 'navigate':
        return await handleNavigate(chrome, url);

      case 'snapshot':
        return await handleSnapshot(chrome);

      case 'screenshot':
        return await handleScreenshot(chrome, options);

      case 'click':
        return await handleClick(chrome, options);

      case 'fill':
        return await handleFill(chrome, options);

      case 'console':
        return await handleConsole(chrome);

      case 'network':
        return await handleNetwork(chrome, options);

      case 'performance':
        return await handlePerformance(chrome, url, options);

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  } catch (error) {
    return {
      result: `Error executing ${action}: ${error}`,
      artifacts: []
    };
  }
}

/**
 * Navigate to URL
 */
async function handleNavigate(
  chrome: ChromeDevToolsMCP,
  url: string
): Promise<SkillOutput> {
  await chrome.navigate_page({ url });

  return {
    result: `Navigated to ${url}`,
    artifacts: []
  };
}

/**
 * Take page snapshot
 */
async function handleSnapshot(
  chrome: ChromeDevToolsMCP
): Promise<SkillOutput> {
  const snapshot = await chrome.take_snapshot();

  return {
    result: 'Page snapshot captured',
    data: {
      snapshot: snapshot.substring(0, 1000) + '...',  // Truncate for output
      length: snapshot.length
    }
  };
}

/**
 * Capture screenshot
 */
async function handleScreenshot(
  chrome: ChromeDevToolsMCP,
  options: any
): Promise<SkillOutput> {
  const filename = options.filename || `screenshot-${Date.now()}.png`;
  const fullPage = options.fullPage || false;

  await chrome.take_screenshot({ filename, fullPage });

  return {
    result: 'Screenshot captured',
    artifacts: [filename]
  };
}

/**
 * Click element
 */
async function handleClick(
  chrome: ChromeDevToolsMCP,
  options: any
): Promise<SkillOutput> {
  if (!options.uid) {
    throw new Error('UID required for click action');
  }

  await chrome.click({ uid: options.uid });

  return {
    result: `Clicked element ${options.uid}`,
    artifacts: []
  };
}

/**
 * Fill input field
 */
async function handleFill(
  chrome: ChromeDevToolsMCP,
  options: any
): Promise<SkillOutput> {
  if (!options.uid || !options.value) {
    throw new Error('UID and value required for fill action');
  }

  await chrome.fill({ uid: options.uid, value: options.value });

  return {
    result: `Filled ${options.uid} with "${options.value}"`,
    artifacts: []
  };
}

/**
 * Check console messages
 */
async function handleConsole(
  chrome: ChromeDevToolsMCP
): Promise<SkillOutput> {
  const messages = await chrome.list_console_messages();
  const errors = messages.filter((m: any) => m.type === 'error');
  const warnings = messages.filter((m: any) => m.type === 'warn');

  return {
    result: `Console: ${messages.length} total, ${errors.length} errors, ${warnings.length} warnings`,
    data: {
      errors,
      warnings,
      total: messages.length
    }
  };
}

/**
 * Monitor network requests
 */
async function handleNetwork(
  chrome: ChromeDevToolsMCP,
  options: any
): Promise<SkillOutput> {
  const requests = await chrome.list_network_requests({
    resourceTypes: options.resourceTypes || ['fetch', 'xhr']
  });

  const failed = requests.filter((r: any) => r.status >= 400);

  return {
    result: `Network: ${requests.length} requests, ${failed.length} failed`,
    data: {
      requests,
      failed,
      total: requests.length
    }
  };
}

/**
 * Run performance analysis
 */
async function handlePerformance(
  chrome: ChromeDevToolsMCP,
  url: string,
  options: any
): Promise<SkillOutput> {
  // Start trace
  await chrome.performance_start_trace({
    reload: true,
    autoStop: true
  });

  // Navigate to page
  await chrome.navigate_page({ url });

  // Wait for page load
  await chrome.wait_for({ time: 3000 });

  // Stop trace
  await chrome.performance_stop_trace();

  // Get insights
  const insights: any = {};

  if (options.insightName) {
    // Get specific insight
    insights[options.insightName] = await chrome.performance_analyze_insight({
      insightName: options.insightName
    });
  } else {
    // Get all core insights
    const insightNames = ['LCPBreakdown', 'CLSCulprits', 'DocumentLatency', 'RenderBlocking'];

    for (const name of insightNames) {
      try {
        insights[name] = await chrome.performance_analyze_insight({ insightName: name });
      } catch (error) {
        insights[name] = `Error: ${error}`;
      }
    }
  }

  return {
    result: 'Performance trace complete',
    data: { insights },
    artifacts: []
  };
}

/**
 * Chrome DevTools MCP interface
 */
export interface ChromeDevToolsMCP {
  navigate_page: (opts: { url: string; timeout?: number }) => Promise<void>;
  take_snapshot: () => Promise<string>;
  take_screenshot: (opts: { filename: string; fullPage?: boolean; uid?: string }) => Promise<void>;
  click: (opts: { uid: string; dblClick?: boolean }) => Promise<void>;
  fill: (opts: { uid: string; value: string }) => Promise<void>;
  list_console_messages: () => Promise<any[]>;
  list_network_requests: (opts?: { resourceTypes?: string[] }) => Promise<any[]>;
  get_network_request: (opts: { url: string }) => Promise<any>;
  performance_start_trace: (opts: { reload?: boolean; autoStop?: boolean }) => Promise<void>;
  performance_stop_trace: () => Promise<void>;
  performance_analyze_insight: (opts: { insightName: string }) => Promise<any>;
  emulate_network: (opts: { throttlingOption: string }) => Promise<void>;
  emulate_cpu: (opts: { throttlingRate: number }) => Promise<void>;
  evaluate_script: (opts: { function: string }) => Promise<any>;
  wait_for: (opts: { text?: string; time?: number; timeout?: number }) => Promise<void>;
  list_pages: () => Promise<any[]>;
  new_page: (opts: { url: string; timeout?: number }) => Promise<void>;
  close_page: (opts: { pageIdx: number }) => Promise<void>;
  select_page: (opts: { pageIdx: number }) => Promise<void>;
  fill_form: (opts: { elements: Array<{ uid: string; value: string }> }) => Promise<void>;
  hover: (opts: { uid: string }) => Promise<void>;
  drag: (opts: { from_uid: string; to_uid: string }) => Promise<void>;
  upload_file: (opts: { uid: string; filePath: string }) => Promise<void>;
  handle_dialog: (opts: { action: 'accept' | 'dismiss'; promptText?: string }) => Promise<void>;
}

/**
 * Example usage
 */
export async function exampleUsage(chrome: ChromeDevToolsMCP) {
  // Navigate
  const navResult = await executeSkill(
    { url: 'http://localhost:8080', action: 'navigate' },
    chrome
  );
  console.log(navResult);

  // Take snapshot
  const snapshotResult = await executeSkill(
    { url: '', action: 'snapshot' },
    chrome
  );
  console.log(snapshotResult);

  // Check console
  const consoleResult = await executeSkill(
    { url: '', action: 'console' },
    chrome
  );
  console.log(consoleResult);

  // Take screenshot
  const screenshotResult = await executeSkill(
    {
      url: '',
      action: 'screenshot',
      options: { filename: 'example.png', fullPage: true }
    },
    chrome
  );
  console.log(screenshotResult);

  // Run performance analysis
  const perfResult = await executeSkill(
    {
      url: 'http://localhost:8080/dashboard',
      action: 'performance',
      options: { insightName: 'LCPBreakdown' }
    },
    chrome
  );
  console.log(perfResult);
}
