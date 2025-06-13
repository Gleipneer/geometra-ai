#!/bin/bash

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Setting up test environment...${NC}"

# Skapa nödvändiga kataloger
mkdir -p tests/{unit,integration,system}
mkdir -p scripts
mkdir -p logs

# Installera Python-beroenden
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio pytest-mock
pip install black flake8 mypy

# Installera Node.js-beroenden
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Skapa grundläggande testkonfiguration
echo -e "${YELLOW}Creating test configuration...${NC}"

# Python test config
cat > pytest.ini << EOL
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=term-missing
EOL

# Jest config
cat > jest.config.js << EOL
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js',
  ],
};
EOL

# Skapa grundläggande testfiler
echo -e "${YELLOW}Creating basic test files...${NC}"

# Python test files
cat > tests/unit/test_environment.py << EOL
"""Test environment configuration."""
import os
import pytest

def test_environment_variables():
    """Test that required environment variables are set."""
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'API_KEY',
    ]
    
    for var in required_vars:
        assert os.getenv(var) is not None, f"Environment variable {var} is not set"

def test_database_connection():
    """Test database connection."""
    # TODO: Implement database connection test
    pass

def test_redis_connection():
    """Test Redis connection."""
    # TODO: Implement Redis connection test
    pass
EOL

# JavaScript test files
cat > src/setupTests.js << EOL
import '@testing-library/jest-dom';
EOL

# Skapa verifieringsskript
echo -e "${YELLOW}Creating verification scripts...${NC}"

cat > scripts/verify_env.sh << EOL
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
EOL

chmod +x scripts/verify_env.sh

# Skapa bootstrap status log
echo -e "${YELLOW}Creating bootstrap status log...${NC}"
cat > logs/bootstrap_status.log << EOL
[$(date)] Test environment setup started
[$(date)] Created directory structure
[$(date)] Installed Python dependencies
[$(date)] Installed Node.js dependencies
[$(date)] Created test configuration
[$(date)] Created basic test files
[$(date)] Created verification scripts
[$(date)] Test environment setup completed
EOL

echo -e "${GREEN}Test environment setup completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run ./scripts/verify_env.sh to verify the setup"
echo "2. Start implementing tests in tests/unit/test_environment.py"
echo "3. Begin with Fas 1.1 implementation" 