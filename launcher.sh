#!/bin/bash

cd "$(dirname "$0")"
source venv/bin/activate
echo "Running the script..."
python3 Fsg_pp.py

# Check the exit code of the previous command
if [ $? -ne 0 ]; then
    echo "An error occurred while running the script."
    read -n 1 -s -r -p "Press any key to exit..."
fi
