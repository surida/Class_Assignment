#!/bin/bash
# Run the Class Assignment GUI using the system python (which has PyQt6 installed)
# usage: ./run.sh

# Ensure we are in the script directory
cd "$(dirname "$0")"

# Run with system python (python3)
/usr/bin/python3 class_assigner_gui_qt.py
