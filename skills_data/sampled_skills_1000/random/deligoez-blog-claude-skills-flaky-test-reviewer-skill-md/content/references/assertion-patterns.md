# Assertion Patterns

## Checklist

- [ ] `assertSame(true, $value)` not `assertTrue($value)` - catches boolean casts
- [ ] `$money->isEqualTo($other)` not `assertEquals` - float precision
- [ ] `assertEqualsWithDelta()` for timestamps - millisecond differences
- [ ] `expectException()` preferred over try/catch
- [ ] Explicit `ORDER BY` for ordered assertions

## Boolean Assertions

`assertTrue()` and `assertFalse()` use loose comparison. Use `assertSame()` to catch missing boolean casts.

```php
// BAD - passes even if $result is "1" or 1
$this->assertTrue($result);

// GOOD - fails if $result is not exactly true
$this->assertSame(true, $result);
$this->assertSame(false, $result);

// Also catches null, empty string, etc.
$this->assertSame(true, $user->isActive()); // Fails if method returns 1
```

## Money Comparison

Never use `assertEquals` for Money objects. Float precision issues cause flaky tests.

```php
// BAD - float comparison issues
$this->assertEquals($expected, $actual);

// GOOD - use Money's comparison methods
$this->assertTrue($price->isEqualTo(Money::EUR(1000)));
$this->assertTrue($total->isGreaterThan(Money::EUR(0)));

// Or convert to cents for comparison
$this->assertSame(1000, $price->getAmount());
```

## Timestamp Assertions

Timestamps may differ by milliseconds. Use delta comparison.

```php
// BAD - fails on millisecond differences
$this->assertEquals($expected->timestamp, $actual->timestamp);

// GOOD - allow 1 second delta
$this->assertEqualsWithDelta(
    $expected->timestamp,
    $actual->timestamp,
    1 // seconds
);

// For Carbon objects
$this->assertTrue($expected->isSameMinute($actual));
```

## Exception Assertions

Prefer `expectException()` over try/catch. More readable and catches assertion order issues.

```php
// BAD - easy to forget assertions in catch block
try {
    $service->process();
    $this->fail('Expected exception');
} catch (ValidationException $e) {
    $this->assertEquals('Invalid', $e->getMessage());
}

// GOOD - declarative
$this->expectException(ValidationException::class);
$this->expectExceptionMessage('Invalid');

$service->process();
```

## Ordered Assertions

When asserting order, ensure the query has explicit ORDER BY. Database order is not guaranteed.

```php
// BAD - order not guaranteed
$users = User::all();
$this->assertEquals('Alice', $users[0]->name);
$this->assertEquals('Bob', $users[1]->name);

// GOOD - explicit order
$users = User::orderBy('name')->get();
$this->assertEquals('Alice', $users[0]->name);
$this->assertEquals('Bob', $users[1]->name);

// Or use assertCount + assertContains for unordered
$this->assertCount(2, $users);
$this->assertTrue($users->contains('name', 'Alice'));
```

## Collection Assertions

For collections, prefer Laravel's collection assertions.

```php
// Instead of checking order
$this->assertEquals(['a', 'b', 'c'], $collection->toArray());

// Use collection methods
$this->assertCount(3, $collection);
$this->assertTrue($collection->contains('a'));
$this->assertEqualsCanonicalizing(['a', 'b', 'c'], $collection->toArray());
```
