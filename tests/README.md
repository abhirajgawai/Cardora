# Tests

This folder contains test scripts for Cardora application.

## Files

- **test_db_connection.py** - Comprehensive database connection tests
  - Tests environment variables
  - Tests database connectivity
  - Tests table creation and queries
  - Tests session dependency injection

- **verify_users_table.py** - Verify users table structure and schema

- **cleanup_test_table.py** - Clean up test tables from database

- **test_postgres_user.py** - Test PostgreSQL user credentials

- **simple_test.py** - Simple connection tests with different password formats

- **verify_user.py** - Quick user verification script

## Running Tests

```bash
# Run database connection tests
python tests/test_db_connection.py

# Verify users table
python tests/verify_users_table.py
```

## Compare to .NET

In .NET, this would be like:
- `Cardora.Tests` project
- Tests using xUnit or NUnit
- Separated into Unit Tests and Integration Tests

In Python:
- `tests/` folder
- Tests use pytest (we'll set this up later)
- Mix of utility scripts and test classes
