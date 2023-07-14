#!/bin/bash

# Define the name of the output zip file and the directory where it should be placed
output_dir="./build"
output_zip="autolab.zip"
output_path="$output_zip"

# Create the output directory if it does not exist
if [ ! -d "$output_dir" ]; then
    mkdir -p $output_dir
fi

# Remove any existing output zip file
if [ -f "$output_path" ]; then
    rm $output_path
fi

# Define directories to exclude
exclude_dirs=("__pycache__" "autolab.egg-info")

# Generate exclude string for zip command
exclude=""
for dir in "${exclude_dirs[@]}"; do
  exclude="$exclude -x \*${dir}\*"
done

# Change to src/ directory and zip its contents (this places the contents at the base of the zip)
cd src/
eval "zip -r ../$output_path ./* $exclude"

# Return to the original directory
cd ..

# Add credentials to the zip
zip -r $output_path credentials/*

# Move the zip file to the output directory
mv $output_zip $output_dir/

# Check the status of the zip operation
if [ $? -eq 0 ]; then
    echo "Successfully created $output_dir/$output_path"
else
    echo "An error occurred while creating $output_dir/$output_path"
    exit 1
fi
