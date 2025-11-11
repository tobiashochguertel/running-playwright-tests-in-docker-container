#!/bin/bash
set -e

# This script allows flexible argument passing to pytest
# It ensures the virtual environment is activated properly

# If no arguments provided, run pytest with default args
# Otherwise, execute the provided command directly
if [ $# -eq 0 ]; then
  exec pytest
else
  exec "$@"
fi
