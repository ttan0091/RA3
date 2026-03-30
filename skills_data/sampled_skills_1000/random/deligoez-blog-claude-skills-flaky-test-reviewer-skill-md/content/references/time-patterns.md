# Time Patterns

## Checklist

- [ ] `travelTo(now()->startOfMinute())` at test start
- [ ] Back-to-back records: pass explicit `created_at` to factory
- [ ] No `now()`, `config()`, facades in DataProviders - run before Laravel boots
- [ ] No natural language parsing (`Date::parse('Today')`) - DST issues
- [ ] `createFromFormat()` always chains `startOfDay()` or `startOfMinute()`

## The createFromFormat Trap

`Carbon::createFromFormat()` preserves whatever time components are not in your format string - which means it uses the current wall clock time.

```php
// BAD - preserves current hour:minute:second
$date = Carbon::createFromFormat('Y-m-d', '2024-01-15');
// If run at 14:32:45, you get 2024-01-15 14:32:45

// GOOD - explicit time reset
$date = Carbon::createFromFormat('Y-m-d', '2024-01-15')->startOfDay();
// Always 2024-01-15 00:00:00
```

## Time Freezing

Use `startOfMinute()` as default. Only use `startOfSecond()` when testing second-level precision.

```php
// Standard freezing
$this->travelTo(now()->startOfMinute());

// Only when testing seconds matter
$this->travelTo(now()->startOfSecond());
```

## Back-to-Back Records

When creating multiple records in sequence, they may have different `created_at` timestamps due to millisecond differences.

```php
// BAD - timestamps may differ by milliseconds
$orders = Order::factory()->count(3)->create();
// Ordering assertions become flaky

// GOOD - explicit timestamp
$timestamp = now();
$orders = Order::factory()->count(3)->create([
    'created_at' => $timestamp
]);
```

## DataProviders Run Before Laravel

DataProviders execute before Laravel boots. No facades, no `now()`, no `config()`.

```php
// BAD - Laravel not booted yet
public static function dateProvider(): array
{
    return [
        [now()->subDays(1)],  // FAILS
        [config('app.date')], // FAILS
    ];
}

// GOOD - use static values or closures
public static function dateProvider(): array
{
    return [
        [fn() => now()->subDays(1)],
        ['2024-01-15'],
    ];
}

public function test_something(Closure|string $date): void
{
    $date = is_callable($date) ? $date() : $date;
    // ...
}
```

## DST and Natural Language

Avoid natural language date parsing - DST transitions cause issues.

```php
// BAD - "today" can be ambiguous during DST
Date::parse('Today');
Date::parse('next monday');

// GOOD - explicit dates
Carbon::parse('2024-01-15');
Carbon::now()->startOfDay();
```
