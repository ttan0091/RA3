# Common Test Patterns

> Reusable testing patterns for specific scenarios

## Testing Async/Await Code

### Python (pytest + asyncio)

```python
import pytest

@pytest.mark.asyncio
async def test_async_data_fetch():
    """Test async function that fetches data."""
    # Arrange
    user_id = 123

    # Act
    result = await fetch_user_data(user_id)

    # Assert
    assert result['id'] == user_id
    assert 'name' in result
```

### JavaScript (jest)

```javascript
describe('fetchUserData', () => {
  test('fetches user data successfully', async () => {
    const userId = 123;
    const result = await fetchUserData(userId);

    expect(result.id).toBe(userId);
    expect(result).toHaveProperty('name');
  });
});
```

## Testing Database Operations

### Using Fixtures for Database State

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope='function')
def db_session():
    """Create a fresh database session for each test."""
    # Setup: create in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Teardown: close and cleanup
    session.close()

def test_create_user(db_session):
    """Test creating a user in database."""
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert db_session.query(User).count() == 1
```

### Mocking Database Calls

```python
from unittest.mock import Mock, patch

def test_get_user_from_db():
    """Test function that queries database."""
    with patch('module.db.query') as mock_query:
        # Arrange
        mock_query.return_value.filter_by.return_value.first.return_value = Mock(
            id=1, name="Test User"
        )

        # Act
        user = get_user_by_id(1)

        # Assert
        assert user.name == "Test User"
        mock_query.assert_called_once()
```

## Testing API Endpoints

### Testing HTTP Requests

```python
import pytest
from unittest.mock import patch
import requests

def test_api_call_success():
    """Test successful API call."""
    with patch('requests.get') as mock_get:
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok', 'data': [1, 2, 3]}
        mock_get.return_value = mock_response

        # Act
        result = fetch_api_data('https://api.example.com/data')

        # Assert
        assert result['status'] == 'ok'
        assert len(result['data']) == 3
        mock_get.assert_called_once_with('https://api.example.com/data')
```

### Testing Flask/FastAPI Endpoints

```python
import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

def test_get_users_endpoint(client):
    """Test GET /users endpoint."""
    response = client.get('/users')

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user_endpoint(client):
    """Test POST /users endpoint."""
    user_data = {'name': 'Test', 'email': 'test@example.com'}
    response = client.post('/users', json=user_data)

    assert response.status_code == 201
    assert response.json()['name'] == 'Test'
```

## Testing File I/O

### Using tmp_path Fixture (pytest)

```python
def test_write_and_read_file(tmp_path):
    """Test writing and reading a file."""
    # Arrange
    test_file = tmp_path / "test.txt"
    content = "Hello, World!"

    # Act
    write_to_file(test_file, content)
    result = read_from_file(test_file)

    # Assert
    assert result == content

def test_process_csv(tmp_path):
    """Test CSV processing."""
    # Arrange
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\nBob,25")

    # Act
    result = process_csv(csv_file)

    # Assert
    assert len(result) == 2
    assert result[0]['name'] == 'Alice'
```

### Mocking File Operations

```python
from unittest.mock import mock_open, patch

def test_read_config():
    """Test reading config file with mocked file."""
    mock_data = "key=value\nfoo=bar"

    with patch('builtins.open', mock_open(read_data=mock_data)):
        config = read_config('config.txt')

        assert config['key'] == 'value'
        assert config['foo'] == 'bar'
```

## Testing Time-Dependent Code

### Freezing Time

```python
from unittest.mock import patch
from datetime import datetime

def test_is_business_hours():
    """Test time-dependent function."""
    # Mock time to be 2PM on a Tuesday
    mock_time = datetime(2024, 1, 2, 14, 0)  # Tuesday 2PM

    with patch('module.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_time

        assert is_business_hours() == True

def test_is_weekend():
    """Test weekend detection."""
    # Mock time to be Saturday
    mock_time = datetime(2024, 1, 6, 10, 0)  # Saturday 10AM

    with patch('module.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_time

        assert is_weekend() == True
```

### Using freezegun Library

```python
from freezegun import freeze_time

@freeze_time("2024-01-15 14:00:00")
def test_create_timestamp():
    """Test function that creates timestamps."""
    result = create_timestamp()
    assert result.day == 15
    assert result.hour == 14
```

## Testing Random/Non-Deterministic Code

### Seeding Random Number Generators

```python
import random
import pytest

def test_random_selection():
    """Test function that uses randomness."""
    random.seed(42)  # Set seed for reproducibility

    items = ['a', 'b', 'c', 'd', 'e']
    result = random_select(items, count=2)

    # With seed 42, we know the result
    assert len(result) == 2
    assert all(item in items for item in result)
```

### Mocking Random

```python
from unittest.mock import patch

def test_random_id_generation():
    """Test ID generation with mocked random."""
    with patch('random.randint', return_value=12345):
        user_id = generate_user_id()
        assert user_id == "USER_12345"
```

## Testing CLI Applications

### Testing with Click (Python)

```python
from click.testing import CliRunner
import pytest
from cli import main

@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()

def test_cli_help(runner):
    """Test --help flag."""
    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert 'Usage:' in result.output

def test_cli_command(runner):
    """Test CLI command execution."""
    result = runner.invoke(main, ['process', '--input', 'test.txt'])

    assert result.exit_code == 0
    assert 'Success' in result.output
```

### Testing argparse

```python
import sys
from unittest.mock import patch

def test_parse_args():
    """Test argument parsing."""
    test_args = ['prog', '--input', 'file.txt', '--verbose']

    with patch.object(sys, 'argv', test_args):
        args = parse_arguments()

        assert args.input == 'file.txt'
        assert args.verbose == True
```

## Testing Classes with State

### Testing State Changes

```python
class TestShoppingCart:
    """Tests for ShoppingCart class."""

    @pytest.fixture
    def cart(self):
        """Create empty cart for each test."""
        return ShoppingCart()

    def test_add_item(self, cart):
        """Test adding item to cart."""
        cart.add_item('apple', price=1.5, quantity=2)

        assert len(cart.items) == 1
        assert cart.total == 3.0

    def test_remove_item(self, cart):
        """Test removing item from cart."""
        cart.add_item('apple', price=1.5, quantity=2)
        cart.remove_item('apple')

        assert len(cart.items) == 0
        assert cart.total == 0.0

    def test_clear_cart(self, cart):
        """Test clearing entire cart."""
        cart.add_item('apple', price=1.5)
        cart.add_item('banana', price=0.8)
        cart.clear()

        assert cart.is_empty()
```

## Testing Generators

```python
def test_number_generator():
    """Test generator function."""
    gen = generate_numbers(start=1, end=5)

    assert next(gen) == 1
    assert next(gen) == 2
    assert next(gen) == 3
    assert next(gen) == 4
    assert next(gen) == 5

    with pytest.raises(StopIteration):
        next(gen)

def test_generator_as_list():
    """Test generator by converting to list."""
    result = list(generate_numbers(start=1, end=5))
    assert result == [1, 2, 3, 4, 5]
```

## Testing Context Managers

```python
def test_context_manager():
    """Test custom context manager."""
    with DatabaseConnection('test.db') as conn:
        assert conn.is_connected
        result = conn.query('SELECT 1')
        assert result is not None

    # After exiting context, connection should be closed
    assert not conn.is_connected

def test_context_manager_error():
    """Test context manager handles errors."""
    with pytest.raises(DatabaseError):
        with DatabaseConnection('invalid.db') as conn:
            pass
```

## Testing Decorators

```python
def test_cache_decorator():
    """Test function with cache decorator."""
    call_count = 0

    @cache
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call with same argument (should use cache)
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count == 1  # Not incremented

    # Different argument
    result3 = expensive_function(10)
    assert result3 == 20
    assert call_count == 2
```

## Testing Error Handling

### Testing Retries

```python
from unittest.mock import Mock, call

def test_retry_on_failure():
    """Test function retries on failure."""
    mock_func = Mock(side_effect=[
        Exception("Fail 1"),
        Exception("Fail 2"),
        "Success"
    ])

    with patch('module.api_call', mock_func):
        result = retry_api_call(max_attempts=3)

        assert result == "Success"
        assert mock_func.call_count == 3
```

### Testing Graceful Degradation

```python
def test_fallback_on_error():
    """Test function falls back gracefully."""
    with patch('module.primary_service', side_effect=Exception("Service down")):
        result = get_data_with_fallback()

        # Should use fallback instead of crashing
        assert result is not None
        assert result.source == 'fallback'
```

## Testing Performance

### Testing Execution Time

```python
import time

def test_function_performance():
    """Test function completes within time limit."""
    start = time.time()

    result = process_large_dataset(data)

    duration = time.time() - start
    assert duration < 5.0, f"Function took {duration}s, expected <5s"
```

### Testing Memory Usage

```python
import sys

def test_memory_efficiency():
    """Test function doesn't create excessive objects."""
    initial_objects = len(gc.get_objects())

    process_data(large_dataset)

    final_objects = len(gc.get_objects())
    growth = final_objects - initial_objects

    assert growth < 1000, f"Created {growth} objects, expected <1000"
```
