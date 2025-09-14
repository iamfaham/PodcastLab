# Podcast Script Generation Test Suite

This directory contains comprehensive tests for the `generate_podcast_script` method from the `PodcastAgent` class.

## Files

- `test_podcast_script.py` - Main test file with comprehensive test cases
- `run_tests.py` - Simple test runner script
- `TEST_README.md` - This documentation file

## Test Coverage

The test suite covers the following scenarios:

### Basic Functionality

- ✅ Basic script generation without search
- ✅ Script generation with search enabled
- ✅ Proper parsing of API responses
- ✅ Grounding metadata extraction

### Edge Cases

- ✅ Response with insufficient parts (< 3)
- ✅ Response with excessive parts (> 3)
- ✅ Empty response handling
- ✅ None response handling
- ✅ API error handling

### Data Processing

- ✅ Script part splitting and cleaning
- ✅ Markdown formatting removal
- ✅ Whitespace normalization
- ✅ Multiple topic testing

### Response Structure Variations

- ✅ `response.text` attribute access
- ✅ `response.candidates[0].content.parts[0].text` structure
- ✅ `response.parts[0].text` structure

## Running the Tests

### Option 1: Using the test runner (Recommended)

```bash
python run_tests.py
```

### Option 2: Using unittest directly

```bash
python test_podcast_script.py
```

### Option 3: Using pytest (if installed)

```bash
pytest test_podcast_script.py -v
```

## Test Requirements

The tests use mocking to avoid making real API calls, so you don't need:

- A valid Google AI API key
- Internet connection
- Real API quota

### Required Dependencies

- `unittest` (built-in)
- `unittest.mock` (built-in)
- `main.py` (the PodcastAgent class)

### Optional Dependencies

- `pytest` (for enhanced test output)

## Test Structure

Each test method follows this pattern:

1. **Setup**: Mock the API response and client
2. **Execute**: Call the `generate_podcast_script` method
3. **Assert**: Verify the expected behavior

### Example Test Method

```python
def test_generate_podcast_script_basic(self):
    """Test basic podcast script generation without search."""
    # Mock the API response
    mock_response = Mock()
    mock_response.text = self.sample_script_response

    self.agent.client.models.generate_content.return_value = mock_response

    # Test the method
    topic = "Artificial Intelligence"
    script_parts, grounding_metadata = self.agent.generate_podcast_script(topic, use_search=False)

    # Assertions
    self.assertIsInstance(script_parts, list)
    self.assertEqual(len(script_parts), 3)
    self.assertIsInstance(grounding_metadata, dict)
```

## Mock Data

The tests use realistic mock data including:

- Sample podcast script with 3 parts
- Grounding metadata with search queries
- Various response structures
- Error scenarios

## Expected Output

When running the tests, you should see output like:

```
🧪 Running Podcast Script Generation Tests 🧪
==================================================
test_generate_podcast_script_api_error (__main__.TestPodcastScriptGeneration) ... ok
test_generate_podcast_script_basic (__main__.TestPodcastScriptGeneration) ... ok
test_generate_podcast_script_different_topics (__main__.TestPodcastScriptGeneration) ... ok
...
==================================================
Tests run: 12
Failures: 0
Errors: 0
Success rate: 100.0%

✅ All tests passed!
```

## Adding New Tests

To add new test cases:

1. Create a new test method starting with `test_`
2. Follow the setup/execute/assert pattern
3. Use descriptive docstrings
4. Mock external dependencies
5. Test both success and failure scenarios

### Example New Test

```python
def test_generate_podcast_script_custom_prompt(self):
    """Test script generation with custom prompt modifications."""
    # Setup mock
    mock_response = Mock()
    mock_response.text = self.sample_script_response
    self.agent.client.models.generate_content.return_value = mock_response

    # Test
    topic = "Custom Topic"
    script_parts, _ = self.agent.generate_podcast_script(topic)

    # Assert
    self.assertEqual(len(script_parts), 3)
    # Add more specific assertions...
```

## Troubleshooting

### Common Issues

1. **ImportError**: Make sure `main.py` is in the same directory
2. **Mock errors**: Check that all API calls are properly mocked
3. **Assertion failures**: Verify expected vs actual values match

### Debug Mode

To run tests with more verbose output:

```bash
python -m unittest test_podcast_script.TestPodcastScriptGeneration.test_generate_podcast_script_basic -v
```

## Integration with CI/CD

These tests can be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Podcast Script Tests
  run: |
    python -m pip install --upgrade pip
    python -m pip install pytest
    python run_tests.py
```

## Performance

The tests are designed to run quickly:

- No real API calls (mocked)
- No file I/O operations
- Minimal external dependencies
- Fast execution (< 5 seconds typically)
