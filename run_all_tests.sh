#!/bin/bash

# Set error handling
set -e
set -o pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python package
install_package() {
    print_status "Installing $1..."
    pip install "$1"
}

# Function to handle test failures
handle_test_failure() {
    print_error "Test sequence failed at: $1"
    print_status "Check bootstrap_status.log for details"
    print_status "To resume from this point, run: python tests/test_sequence.py --start-from $1"
    exit 1
}

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check and install required Python packages
required_packages=(
    "pytest"
    "pytest-cov"
    "pytest-mock"
    "pytest-asyncio"
    "pytest-xdist"
)

for package in "${required_packages[@]}"; do
    if ! python3 -c "import ${package//-/_}" 2>/dev/null; then
        print_warning "$package not found, installing..."
        install_package "$package"
    fi
done

# Set PYTHONPATH to project root
export PYTHONPATH=$(pwd)
print_status "Set PYTHONPATH to: $PYTHONPATH"

# Create logs directory if it doesn't exist
mkdir -p logs
print_status "Created logs directory"

# Run cleanup
print_status "Running cleanup..."
if ! python3 tests/cleanup.py; then
    print_error "Cleanup failed"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    print_warning ".env file not found"
    print_status "Creating .env file from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        print_status "Created .env file from template"
    else
        print_error ".env.template not found"
        exit 1
    fi
fi

# Verify test files exist
print_status "Verifying test files..."
missing_tests=0
for test_file in tests/unit/*/test_*.py; do
    if [ ! -f "$test_file" ]; then
        print_warning "Missing test file: $test_file"
        missing_tests=$((missing_tests + 1))
    fi
done

if [ $missing_tests -gt 0 ]; then
    print_warning "Found $missing_tests missing test files"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Test sequence aborted"
        exit 1
    fi
fi

# Run the test sequence
print_status "Starting test sequence..."
python3 tests/test_sequence.py

# Check the exit status
if [ $? -eq 0 ]; then
    print_status "All tests completed successfully"
    exit 0
else
    handle_test_failure "$(tail -n 1 bootstrap_status.log | cut -d' ' -f4-)"
fi 