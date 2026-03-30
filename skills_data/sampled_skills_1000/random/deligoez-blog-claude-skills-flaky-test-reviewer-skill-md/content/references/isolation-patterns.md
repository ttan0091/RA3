# Isolation Patterns

## Checklist

- [ ] `Storage::fake()` for file operations
- [ ] Observable events: `Model::withoutEvents()` or surgical control
- [ ] Sushi models: use `RefreshesSushiModels` trait
- [ ] Custom cleanup BEFORE `parent::tearDown()`
- [ ] Use opt-in traits for targeted cleanup, not base TestCase

## Storage Fake

Always fake storage for file operations. Real filesystem causes cross-test pollution.

```php
// Setup
Storage::fake('local');

// Test
$response = $this->post('/upload', ['file' => $file]);

// Assert
Storage::disk('local')->assertExists('uploads/file.jpg');
```

## Observable Events

Model observers can trigger external calls (API, notifications, cache updates). Control them surgically.

```php
// Option 1: Disable all events for a model
User::withoutEvents(function () {
    User::factory()->create();
});

// Option 2: Disable specific events
Model::ignoreObservableEvents(['created', 'updated']);
try {
    // Your test code
} finally {
    Model::observeObservableEvents(['created', 'updated']);
}

// Option 3: Fake the side effect
Notification::fake();
$user = User::factory()->create();
```

### Risk Assessment

| Risk | Examples | Action |
|------|----------|--------|
| HIGH | External API calls, notifications, webhooks | Always disable in tests |
| MEDIUM | Cache updates, search index, DB side-effects | Disable unless testing |
| LOW | UUID generation, timestamp setting | Usually safe to keep |

## Sushi Models (Static Data)

Sushi models use static SQLite connections that persist across tests.

```php
// In your TestCase
use Calebporzio\Sushi\Concerns\RefreshesSushiModels;

class TestCase extends BaseTestCase
{
    use RefreshesSushiModels;

    protected function setUp(): void
    {
        parent::setUp();
        $this->refreshSushiModels([
            Country::class,
            Currency::class,
        ]);
    }
}
```

## TearDown Order

Custom cleanup must happen BEFORE `parent::tearDown()`. Parent method clears the container.

```php
protected function tearDown(): void
{
    // Custom cleanup FIRST
    Mockery::close();
    $this->cleanupTestFiles();

    // Parent cleanup LAST
    parent::tearDown();
}
```

## Opt-in Traits vs Base TestCase

Don't put everything in base TestCase. Use opt-in traits for targeted cleanup.

```php
// BAD - every test pays the cost
class TestCase extends BaseTestCase
{
    protected function tearDown(): void
    {
        $this->cleanupS3();        // Slow!
        $this->resetSearchIndex(); // Every test!
        parent::tearDown();
    }
}

// GOOD - opt-in via traits
trait CleansS3
{
    protected function tearDownCleansS3(): void
    {
        Storage::disk('s3')->deleteDirectory('test-uploads');
    }
}

class UploadTest extends TestCase
{
    use CleansS3; // Only tests that need it
}
```

## Passport and Authentication

When using Laravel Passport, always include required scopes.

```php
// BAD - no scopes, will get 403 on scope-protected routes
Passport::actingAs($user);

// GOOD - explicit scopes
Passport::actingAs($user, ['read-orders', 'write-orders']);
```
