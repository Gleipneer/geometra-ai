#!/bin/bash

# Verifiera miljövariabler
echo "Verifying environment variables..."
python -c "import os; assert all(os.getenv(var) for var in ['DATABASE_URL', 'REDIS_URL', 'API_KEY']), 'Missing environment variables'"

# Verifiera Python-miljö
echo "Verifying Python environment..."
python -c "import pytest, black, flake8, mypy"

# Verifiera Node.js-miljö
echo "Verifying Node.js environment..."
node -e "require('jest'); require('@testing-library/react'); require('@testing-library/jest-dom')"

echo "Environment verification complete!"
