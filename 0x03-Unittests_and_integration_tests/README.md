# Unit Testing Project

This project contains unit tests for utility functions, focusing on testing nested map access functionality.

## Files

- `utils.py`: Contains utility functions including `access_nested_map`
- `test_utils.py`: Unit tests for the utils module
- `client.py`: Client module (to be implemented)
- `fixtures.py`: Test fixtures (to be implemented)

## Requirements

- Python 3.7+ on Ubuntu 18.04 LTS
- pycodestyle compliance
- All functions must be type-annotated
- Comprehensive documentation for all modules, classes, and functions

## Running Tests

```bash
python3 -m unittest test_utils.py
```

## Testing Framework

Uses `unittest` with `parameterized` decorators for efficient test parameterization.
