# Test Run Sequence

This document describes the test sequence for the Geometra AI system, which ensures that all components are tested in the correct order and that dependencies are properly managed.

## Overview

The test sequence is managed by `tests/test_sequence.py`, which orchestrates the execution of all test suites in a specific order that follows the system's development flow. Each test suite is executed only when its dependencies have passed successfully.

## Test Sequence

The tests are executed in the following order:

1. System Overview
2. Project Setup
3. Memory Configuration
4. Backend Setup
5. Frontend Setup
6. AI Setup
7. AI Routing
8. Fallback Logic
9. System Check
10. Testing Setup
11. CI Setup
12. CD Setup
13. Post-Deployment Monitoring
14. Security
15. Documentation
16. Backup
17. Disaster Recovery
18. Architecture Diagrams

## Running the Tests

To run the entire test sequence:

```bash
# Set PYTHONPATH to project root
export PYTHONPATH=$(pwd)

# Run the test sequence
python tests/test_sequence.py
```

## Status Logging

The test sequence logs its progress to `bootstrap_status.log` with the following format:

```
[timestamp] - level - message
```

Status messages are color-coded in the console:
- Green: Information and success messages
- Yellow: Warnings
- Red: Errors

## Error Handling

If a test suite fails:
1. The sequence is paused
2. An error message is logged
3. The system waits for user intervention
4. The error details are written to `bootstrap_status.log`

## Dependencies

Each test suite has dependencies that must be satisfied before it can run. The dependencies are defined in the `test_suites` list in `test_sequence.py`. For example:

```python
{
    'name': 'Backend Setup',
    'path': 'tests/unit/backend/test_backend_setup.py',
    'dependencies': ['Memory Configuration']
}
```

## Adding New Tests

To add a new test suite:

1. Create the test file in the appropriate directory under `tests/unit/`
2. Add the test suite to the `test_suites` list in `test_sequence.py`
3. Define its dependencies
4. Ensure the test file follows the project's testing standards

## Troubleshooting

If you encounter issues:

1. Check `bootstrap_status.log` for detailed error messages
2. Verify that all dependencies are installed
3. Ensure PYTHONPATH is set correctly
4. Check that all required files and directories exist

## Best Practices

1. Always run the full test sequence before deploying
2. Monitor `bootstrap_status.log` for warnings and errors
3. Fix failing tests before proceeding to dependent tests
4. Keep test dependencies up to date
5. Document any changes to the test sequence

## Maintenance

The test sequence should be maintained by:

1. Updating dependencies when new features are added
2. Adding new test suites as needed
3. Removing obsolete tests
4. Keeping the documentation current
5. Monitoring test execution times 