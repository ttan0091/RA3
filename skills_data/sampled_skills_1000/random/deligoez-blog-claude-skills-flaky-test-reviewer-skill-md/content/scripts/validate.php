#!/usr/bin/env php
<?php

/**
 * Flaky Test Pattern Detector
 *
 * Scans PHP test files for common flakiness patterns using regex.
 * For more accurate detection, consider using nikic/php-parser for AST analysis.
 *
 * Usage: php validate.php <TestFile.php>
 */

$file = $argv[1] ?? null;

if (!$file) {
    echo "Usage: php validate.php <TestFile.php>\n";
    exit(1);
}

if (!file_exists($file)) {
    echo "Error: File not found: $file\n";
    exit(1);
}

$content = file_get_contents($file);
$lines = explode("\n", $content);
$issues = [];

// Helper to find line number
function findLineNumber(array $lines, string $pattern): ?int
{
    foreach ($lines as $num => $line) {
        if (preg_match($pattern, $line)) {
            return $num + 1;
        }
    }
    return null;
}

// HIGH Priority Patterns
// ----------------------

// Alias mocks
if (preg_match("/Mockery::mock\(['\"]alias:/", $content)) {
    $line = findLineNumber($lines, "/Mockery::mock\(['\"]alias:/");
    $issues[] = [
        'priority' => 'HIGH',
        'line' => $line,
        'pattern' => 'alias mock',
        'message' => 'alias: mock detected - breaks parallel tests. Use container binding instead.',
    ];
}

// Overload mocks
if (preg_match("/Mockery::mock\(['\"]overload:/", $content)) {
    $line = findLineNumber($lines, "/Mockery::mock\(['\"]overload:/");
    $issues[] = [
        'priority' => 'HIGH',
        'line' => $line,
        'pattern' => 'overload mock',
        'message' => 'overload: mock detected - breaks parallel tests. Use container binding instead.',
    ];
}

// createFromFormat without startOfDay/startOfMinute
if (preg_match("/createFromFormat\([^)]+\)/", $content)) {
    if (!preg_match("/createFromFormat\([^)]+\)->startOf/", $content)) {
        $line = findLineNumber($lines, "/createFromFormat\(/");
        $issues[] = [
            'priority' => 'HIGH',
            'line' => $line,
            'pattern' => 'createFromFormat trap',
            'message' => 'createFromFormat() without startOfDay() - preserves wall clock time.',
        ];
    }
}

// Http::sequence
if (preg_match("/Http::sequence\(\)/", $content)) {
    $line = findLineNumber($lines, "/Http::sequence/");
    $issues[] = [
        'priority' => 'HIGH',
        'line' => $line,
        'pattern' => 'Http::sequence',
        'message' => 'Http::sequence() in tests - responses consumed unpredictably in parallel.',
    ];
}

// MEDIUM Priority Patterns
// ------------------------

// No time freezing
if (!preg_match("/travelTo|Carbon::setTestNow|freezeTime/", $content)) {
    if (preg_match("/now\(\)|Carbon::(now|today|parse)/", $content)) {
        $issues[] = [
            'priority' => 'MEDIUM',
            'line' => null,
            'pattern' => 'no time freezing',
            'message' => 'Uses time-dependent code but no travelTo() detected.',
        ];
    }
}

// Direct shouldReceive on facade without partialMock
if (preg_match("/^[^\/]*(?<!partialMock\(\)->)shouldReceive\(/m", $content)) {
    // Check if there's a partialMock call nearby
    if (!preg_match("/partialMock\(\)\s*->\s*shouldReceive/", $content)) {
        if (preg_match("/(Config|Cache|Queue|Mail|Event|Bus)::.*shouldReceive/", $content)) {
            $line = findLineNumber($lines, "/shouldReceive\(/");
            $issues[] = [
                'priority' => 'MEDIUM',
                'line' => $line,
                'pattern' => 'facade mock',
                'message' => 'shouldReceive() on facade without partialMock(). Use Facade::partialMock()->shouldReceive().',
            ];
        }
    }
}

// Bus::fake() without specific jobs
if (preg_match("/Bus::fake\(\)/", $content) && !preg_match("/Bus::fake\(\[[^\]]+\]\)/", $content)) {
    $line = findLineNumber($lines, "/Bus::fake\(\)/");
    $issues[] = [
        'priority' => 'MEDIUM',
        'line' => $line,
        'pattern' => 'global Bus::fake',
        'message' => 'Bus::fake() without specific jobs - consider partial fake: Bus::fake([SpecificJob::class]).',
    ];
}

// Event::fake() without specific events
if (preg_match("/Event::fake\(\)/", $content) && !preg_match("/Event::fake\(\[[^\]]+\]\)/", $content)) {
    $line = findLineNumber($lines, "/Event::fake\(\)/");
    $issues[] = [
        'priority' => 'MEDIUM',
        'line' => $line,
        'pattern' => 'global Event::fake',
        'message' => 'Event::fake() without specific events - consider partial fake.',
    ];
}

// LOW Priority Patterns
// ---------------------

// assertTrue instead of assertSame(true, ...)
if (preg_match("/assertTrue\(\\\$[^)]+\)/", $content)) {
    $line = findLineNumber($lines, "/assertTrue\(\\\$/");
    $issues[] = [
        'priority' => 'LOW',
        'line' => $line,
        'pattern' => 'assertTrue',
        'message' => 'assertTrue($var) - consider assertSame(true, $var) to catch non-boolean returns.',
    ];
}

// assertEquals for potential Money objects
if (preg_match("/assertEquals\([^)]*[Mm]oney|[Pp]rice|[Aa]mount/", $content)) {
    $line = findLineNumber($lines, "/assertEquals\([^)]*[Mm]oney/i");
    $issues[] = [
        'priority' => 'LOW',
        'line' => $line,
        'pattern' => 'Money assertEquals',
        'message' => 'assertEquals() with Money - use $money->isEqualTo() for float safety.',
    ];
}

// Output Results
// --------------

echo "\n";
echo "Flaky Test Pattern Detector\n";
echo "===========================\n";
echo "File: $file\n";
echo "\n";

if (empty($issues)) {
    echo "\033[32m✅ No obvious flaky patterns detected.\033[0m\n";
    echo "\nNote: This is a regex-based scan. Some patterns may not be detected.\n";
    echo "For comprehensive analysis, consider nikic/php-parser for AST-based detection.\n";
    exit(0);
}

// Group by priority
$grouped = ['HIGH' => [], 'MEDIUM' => [], 'LOW' => []];
foreach ($issues as $issue) {
    $grouped[$issue['priority']][] = $issue;
}

$colors = [
    'HIGH' => "\033[31m",   // Red
    'MEDIUM' => "\033[33m", // Yellow
    'LOW' => "\033[36m",    // Cyan
];
$reset = "\033[0m";

foreach (['HIGH', 'MEDIUM', 'LOW'] as $priority) {
    if (empty($grouped[$priority])) {
        continue;
    }

    echo "{$colors[$priority]}[$priority]{$reset}\n";
    foreach ($grouped[$priority] as $issue) {
        $lineInfo = $issue['line'] ? " (line {$issue['line']})" : '';
        echo "  • {$issue['message']}{$lineInfo}\n";
    }
    echo "\n";
}

$total = count($issues);
$high = count($grouped['HIGH']);
$medium = count($grouped['MEDIUM']);
$low = count($grouped['LOW']);

echo "---\n";
echo "Summary: {$total} issue(s) found";
echo " (HIGH: {$high}, MEDIUM: {$medium}, LOW: {$low})\n";
echo "\nNote: This is a regex-based scan. For comprehensive analysis,\n";
echo "consider using nikic/php-parser for AST-based detection.\n";

exit($high > 0 ? 2 : ($medium > 0 ? 1 : 0));
