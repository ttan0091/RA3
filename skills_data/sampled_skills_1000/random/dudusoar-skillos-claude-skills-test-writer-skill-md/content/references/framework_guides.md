# Testing Framework Quick Reference

> Quick reference for common testing frameworks

## pytest (Python)

### Basic Usage

```bash
# Install
pip install pytest

# Run all tests
pytest

# Run specific file
pytest test_module.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=module tests/
```

### Key Features

**Fixtures:**
```python
@pytest.fixture
def sample_data():
    """Reusable test data."""
    return [1, 2, 3]

def test_with_fixture(sample_data):
    assert len(sample_data) == 3
```

**Parametrize:**
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

**Markers:**
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

**Async tests:**
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
    assert result == expected
```

## unittest (Python)

### Basic Usage

```python
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        """Run before each test."""
        self.calc = Calculator()

    def tearDown(self):
        """Run after each test."""
        self.calc = None

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_exception(self):
        with self.assertRaises(ValueError):
            self.calc.divide(1, 0)

if __name__ == '__main__':
    unittest.main()
```

### Assertions

- `assertEqual(a, b)` - a == b
- `assertNotEqual(a, b)` - a != b
- `assertTrue(x)` - bool(x) is True
- `assertFalse(x)` - bool(x) is False
- `assertIs(a, b)` - a is b
- `assertIn(a, b)` - a in b
- `assertRaises(exc)` - raises exc
- `assertAlmostEqual(a, b)` - round(a-b, 7) == 0

## jest (JavaScript)

### Basic Usage

```bash
# Install
npm install --save-dev jest

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Test Structure

```javascript
describe('Calculator', () => {
  test('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('handles null', () => {
    expect(add(null, 5)).toBeNull();
  });
});
```

### Matchers

```javascript
// Equality
expect(value).toBe(4)
expect(value).toEqual({ a: 1, b: 2 })

// Truthiness
expect(value).toBeTruthy()
expect(value).toBeFalsy()
expect(value).toBeNull()
expect(value).toBeUndefined()

// Numbers
expect(value).toBeGreaterThan(3)
expect(value).toBeLessThan(5)
expect(value).toBeCloseTo(0.3)

// Strings
expect(value).toMatch(/pattern/)

// Arrays
expect(array).toContain('item')
expect(array).toHaveLength(3)

// Exceptions
expect(() => fn()).toThrow()
expect(() => fn()).toThrow(Error)
expect(() => fn()).toThrow('error message')
```

### Async Testing

```javascript
// Using promises
test('async test', () => {
  return fetchData().then(data => {
    expect(data).toBe('value');
  });
});

// Using async/await
test('async test', async () => {
  const data = await fetchData();
  expect(data).toBe('value');
});
```

### Mocking

```javascript
// Mock function
const mockFn = jest.fn();
mockFn.mockReturnValue(42);

// Mock module
jest.mock('./module');
import { function } from './module';
function.mockImplementation(() => 'mocked');

// Spy on method
const spy = jest.spyOn(object, 'method');
```

## mocha + chai (JavaScript)

### Basic Usage

```bash
npm install --save-dev mocha chai
```

```javascript
const { expect } = require('chai');

describe('Calculator', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).to.equal(5);
  });

  it('should handle arrays', () => {
    expect([1, 2, 3]).to.have.lengthOf(3);
    expect([1, 2, 3]).to.include(2);
  });
});
```

### Chai Assertions

```javascript
// Expect/Should
expect(foo).to.equal('bar')
foo.should.equal('bar')

// Deep equality
expect(obj).to.deep.equal({ a: 1 })

// Type checking
expect('test').to.be.a('string')
expect({ a: 1 }).to.be.an('object')

// Existence
expect(foo).to.exist
expect(foo).to.be.null
expect(foo).to.be.undefined

// Comparison
expect(10).to.be.above(5)
expect(5).to.be.below(10)

// Arrays/Strings
expect([1, 2, 3]).to.include(2)
expect('foobar').to.contain('foo')
expect([1, 2, 3]).to.have.lengthOf(3)
```

## Configuration Files

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### jest.config.js

```javascript
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.test.{js,jsx}',
  ],
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],
};
```
