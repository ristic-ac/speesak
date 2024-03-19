#!/bin/bash
# Convert all .xls files to .xlsx files
# xls files are in xls/ directory and xlsx files should be saved in xlsx/ directory

# Create xlsx directory if it doesn't exist
mkdir -p xlsx

# Convert all .xls files to .xlsx files using command such as libreoffice --convert-to xlsx my.xls --headless
for file in xls/*.xls; do
  libreoffice --convert-to xlsx --outdir xlsx "$file" --headless
done

# Print message
echo "All .xls files are converted to .xlsx files"
