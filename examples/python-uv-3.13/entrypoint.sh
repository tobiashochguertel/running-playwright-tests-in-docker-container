#!/bin/bash
set -e

# This script allows flexible argument passing to pytest
# It ensures the virtual environment is activated properly

# Execute pytest with all arguments passed to this script
exec pytest "$@"
