# Mocking Guide

> Strategies for mocking dependencies and external services

## When to Mock

**Mock when:**
- Testing code that calls external services (APIs, databases)
- Testing code with slow operations (network, file I/O)
- Testing error conditions that are hard to reproduce
- Isolating unit under test from dependencies

**Don't mock when:**
- Testing integration between components
- Mocking would be more complex than real implementation
- Testing trivial code (getters, setters)

## Python Mocking (unittest.mock)

### Basic Mock Objects

```python
from unittest.mock import Mock

# Create mock
mock_api = Mock()

# Set return value
mock_api.get_user.return_value = {'id': 1, 'name': 'Test'}

# Use in test
result = mock_api.get_user(1)
assert result['name'] == 'Test'

# Verify call
mock_api.get_user.assert_called_once_with(1)
```

### Patching

**Patch function:**
```python
from unittest.mock import patch

def test_fetch_data():
    with patch('module.requests.get') as mock_get:
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'value'}

        # Act
        result = fetch_data('https://api.example.com')

        # Assert
        assert result == {'data': 'value'}
        mock_get.assert_called_once()
```

**Patch as decorator:**
```python
@patch('module.database.query')
def test_get_user(mock_query):
    mock_query.return_value = [{'id': 1}]
    result = get_user(1)
    assert result['id'] == 1
```

**Patch multiple:**
```python
@patch('module.service2')
@patch('module.service1')
def test_multiple(mock_service1, mock_service2):
    # Note: patches are applied bottom-up
    pass
```

### Mock Return Values

```python
# Simple return value
mock.return_value = 42

# Side effect (different return each call)
mock.side_effect = [1, 2, 3]
result1 = mock()  # Returns 1
result2 = mock()  # Returns 2

# Raise exception
mock.side_effect = ValueError("Error")

# Call real function
mock.side_effect = lambda x: x * 2
```

### Mock Attributes

```python
mock_user = Mock()
mock_user.name = "Test"
mock_user.age = 30
mock_user.is_admin = True

# Use spec to limit attributes
mock_user = Mock(spec=['name', 'age'])
mock_user.name = "Test"  # OK
mock_user.invalid = "value"  # Raises AttributeError
```

### Assertions on Mocks

```python
# Called
mock.assert_called()
mock.assert_called_once()

# Called with specific arguments
mock.assert_called_with(arg1, arg2)
mock.assert_called_once_with(arg1, kwarg=value)

# Any call with arguments
mock.assert_any_call(arg1)

# Number of calls
assert mock.call_count == 3

# Get call arguments
call_args = mock.call_args
call_args_list = mock.call_args_list
```

### Mocking Class Instances

```python
@patch('module.DatabaseConnection')
def test_with_db(MockDatabase):
    # Create mock instance
    mock_db_instance = MockDatabase.return_value
    mock_db_instance.query.return_value = [1, 2, 3]

    # Test code that uses DatabaseConnection
    result = function_using_db()

    # Verify
    MockDatabase.assert_called_once()
    mock_db_instance.query.assert_called()
```

### MagicMock

```python
from unittest.mock import MagicMock

# Supports magic methods (__len__, __iter__, etc.)
mock = MagicMock()
len(mock)  # Works
for item in mock:  # Works
    pass
```

## JavaScript Mocking (jest)

### Mock Functions

```javascript
// Create mock
const mockFn = jest.fn();

// Set return value
mockFn.mockReturnValue(42);

// Use
const result = mockFn();
expect(result).toBe(42);

// Verify
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(arg);
```

### Mock Implementations

```javascript
const mockFn = jest.fn((x) => x * 2);
expect(mockFn(5)).toBe(10);

// Different return each call
mockFn
  .mockReturnValueOnce(1)
  .mockReturnValueOnce(2)
  .mockReturnValue(3);

// Async mock
mockFn.mockResolvedValue('async result');
await expect(mockFn()).resolves.toBe('async result');

// Reject
mockFn.mockRejectedValue(new Error('failed'));
```

### Mocking Modules

```javascript
// Auto-mock entire module
jest.mock('./module');

import { function1, function2 } from './module';

// All exports are now mocks
function1.mockReturnValue('mocked');

// Manual mock
jest.mock('./module', () => ({
  function1: jest.fn(() => 'custom mock'),
  function2: jest.fn(),
}));
```

### Spying

```javascript
// Spy on existing method
const spy = jest.spyOn(object, 'method');

// Spy and mock implementation
spy.mockImplementation(() => 'mocked');

// Restore original
spy.mockRestore();
```

### Mocking Timers

```javascript
// Use fake timers
jest.useFakeTimers();

setTimeout(() => callback(), 1000);

// Fast-forward time
jest.advanceTimersByTime(1000);

// Run all timers
jest.runAllTimers();

// Restore real timers
jest.useRealTimers();
```

### Mocking Modules

```javascript
// __mocks__ directory structure
/*
project/
├── src/
│   └── api.js
└── __mocks__/
    └── api.js
*/

// __mocks__/api.js
export const fetchData = jest.fn(() => Promise.resolve('mocked data'));

// In test
jest.mock('../src/api');
import { fetchData } from '../src/api';

test('uses mocked API', async () => {
  const data = await fetchData();
  expect(data).toBe('mocked data');
});
```

## Common Mocking Patterns

### Mocking HTTP Requests

**Python:**
```python
@patch('requests.get')
def test_api_call(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'key': 'value'}
    mock_get.return_value = mock_response

    result = make_api_request()
    assert result['key'] == 'value'
```

**JavaScript:**
```javascript
global.fetch = jest.fn(() =>
  Promise.resolve({
    status: 200,
    json: () => Promise.resolve({ key: 'value' }),
  })
);

test('API call', async () => {
  const result = await makeApiRequest();
  expect(result.key).toBe('value');
});
```

### Mocking Database

**Python:**
```python
@patch('module.db.session')
def test_database_query(mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = {
        'id': 1,
        'name': 'Test'
    }

    result = get_user_by_id(1)
    assert result['name'] == 'Test'
```

**JavaScript:**
```javascript
jest.mock('./db', () => ({
  query: jest.fn(() => Promise.resolve([
    { id: 1, name: 'Test' }
  ])),
}));
```

### Mocking File System

**Python:**
```python
from unittest.mock import mock_open, patch

def test_read_file():
    mock_file_content = "test content"

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = read_config_file('config.txt')
        assert result == mock_file_content
```

**JavaScript:**
```javascript
jest.mock('fs');
import fs from 'fs';

test('reads file', () => {
  fs.readFileSync.mockReturnValue('file content');

  const result = readConfig('config.txt');
  expect(result).toBe('file content');
});
```

### Mocking Environment Variables

**Python:**
```python
@patch.dict('os.environ', {'API_KEY': 'test_key'})
def test_with_env_var():
    assert os.environ['API_KEY'] == 'test_key'
```

**JavaScript:**
```javascript
const originalEnv = process.env;

beforeEach(() => {
  process.env = { ...originalEnv, API_KEY: 'test_key' };
});

afterEach(() => {
  process.env = originalEnv;
});
```

### Partial Mocking

**Python:**
```python
from unittest.mock import Mock

# Mock only specific methods
real_object = RealClass()
real_object.method_to_mock = Mock(return_value='mocked')

# Other methods work normally
real_result = real_object.other_method()
mocked_result = real_object.method_to_mock()
```

**JavaScript:**
```javascript
import * as module from './module';

// Spy on one function, keep others real
jest.spyOn(module, 'specificFunction').mockReturnValue('mocked');

// Other functions work normally
```

## Best Practices

### 1. Mock at the Right Level
```python
# Good - mock at the boundary
@patch('module.external_api.call')
def test_function(mock_api):
    pass

# Avoid - mocking internal implementation
@patch('module.internal_helper')
def test_function(mock_helper):
    pass  # Too low-level
```

### 2. Use Fixtures for Common Mocks
```python
@pytest.fixture
def mock_database():
    with patch('module.db') as mock_db:
        mock_db.query.return_value = []
        yield mock_db

def test_with_db(mock_database):
    # Use fixture
    pass
```

### 3. Verify Interactions
```python
def test_calls_api_correctly():
    with patch('module.api.post') as mock_post:
        function_under_test()

        # Verify called with correct arguments
        mock_post.assert_called_once_with(
            'https://api.example.com/endpoint',
            json={'key': 'value'},
            headers={'Authorization': 'Bearer token'}
        )
```

### 4. Don't Over-Mock
```python
# Good - test real integration
def test_user_service():
    service = UserService(real_database)
    result = service.create_user('name')
    assert result.name == 'name'

# Avoid unless necessary
def test_user_service_with_mocks():
    mock_db = Mock()
    service = UserService(mock_db)
    # Too many mocks, not testing much
```

### 5. Clear Mock State Between Tests
```python
@pytest.fixture(autouse=True)
def reset_mocks():
    yield
    # Clear all mocks after each test
    for mock in [mock1, mock2]:
        mock.reset_mock()
```
