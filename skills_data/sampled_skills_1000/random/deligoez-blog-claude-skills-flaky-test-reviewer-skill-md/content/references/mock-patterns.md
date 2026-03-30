# Mock Patterns

## Checklist

- [ ] No `Mockery::mock('alias:...')` or `overload:` - breaks parallel tests
- [ ] `partialMock()` before `shouldReceive()` on facades
- [ ] Container binding for external services, not alias mocks
- [ ] Partial fakes: `Bus::fake([SpecificJob::class])` - let others run
- [ ] Don't mock inside `Bus::fake()` jobs - internals don't run
- [ ] No `Http::sequence()` in parallel tests - responses consumed unpredictably

## Alias Mocks Break Parallel Tests

Alias mocks (`alias:` and `overload:`) modify global state that persists across tests when running in parallel.

```php
// BAD - global state pollution
Mockery::mock('alias:App\Services\PaymentGateway')
    ->shouldReceive('charge')
    ->andReturn(true);

// GOOD - container binding
$this->app->bind(PaymentGateway::class, function () {
    return new FakePaymentGateway();
});
```

## Facade Mocking

Never call `shouldReceive()` directly on facades. Use `partialMock()` first.

```php
// BAD - may not work reliably
Config::shouldReceive('get')->andReturn('value');

// GOOD - partialMock first
Config::partialMock()
    ->shouldReceive('get')
    ->with('app.key')
    ->andReturn('value');
```

## Cache Before Mock

If a value is cached, the mock never gets called. Clear cache first.

```php
// BAD - cache wins
Config::partialMock()->shouldReceive('get')->andReturn(false);
// But cached value is still returned!

// GOOD - clear cache first
cache()->forget('config.key');
Config::partialMock()->shouldReceive('get')->andReturn(false);
```

## Partial Fakes

Don't fake everything. Only fake what you're testing.

```php
// BAD - all jobs are faked
Bus::fake();
// Unrelated jobs that should run are now silent

// GOOD - only fake specific jobs
Bus::fake([SendWelcomeEmail::class]);
// Other jobs dispatch and run normally
```

Same applies to events:

```php
// Partial event fake
Event::fake([OrderCreated::class]);
// Other events still fire normally
```

## Http::sequence() in Parallel

`Http::sequence()` responses are consumed globally. In parallel tests, wrong test may consume the response.

```php
// BAD in parallel tests
Http::fake([
    'api.example.com/*' => Http::sequence()
        ->push(['status' => 'ok'])
        ->push(['status' => 'error']),
]);

// GOOD - use callbacks for dynamic responses
Http::fake([
    'api.example.com/*' => function ($request) {
        return Http::response(['status' => 'ok']);
    },
]);
```

## Fakes Before Factory

Factory `afterCreating` callbacks run immediately. If they trigger notifications/events, fake them first.

```php
// BAD - notification sent before fake
$user = User::factory()->create(); // afterCreating sends welcome email
Notification::fake(); // Too late!

// GOOD - fake first
Notification::fake();
$user = User::factory()->create();
Notification::assertSent(WelcomeEmail::class);
```
