#!/bin/bash

# Directory setup
TARGET_DIR="folderify_test"

# Create or clean the target directory
if [ -d "$TARGET_DIR" ]; then
    echo "INFO: Cleaning existing directory $TARGET_DIR"
    rm -rf "$TARGET_DIR"
fi

# Create main directory
mkdir -p "$TARGET_DIR"
echo "INFO: Directory $TARGET_DIR created."

# Batch 1: Create nested empty folders
echo "INFO: Creating nested empty folders..."
mkdir -p "$TARGET_DIR/Delete_empty_folder_01/Delete_empty_folder_02/Delete_empty_folder_03"
echo "INFO: Nested empty folders created."

# Batch 2: Create Merge_folder with files and subfolders
echo "INFO: Creating Merge_folder and associated files..."
MERGE_DIR="$TARGET_DIR/Merge_folder"
mkdir -p "$MERGE_DIR"

for YEAR in {2020..2030}; do
    mkdir -p "$MERGE_DIR/$YEAR"
done

for YEAR in {2020..2022}; do
    for MONTH in {01..12}; do
        touch "$MERGE_DIR/${YEAR}_${MONTH}.txt"
        touch "$MERGE_DIR/${YEAR}_${MONTH}.png"
        echo "INFO: Created files ${YEAR}_${MONTH}.txt and ${YEAR}_${MONTH}.png"
    done
done
echo "INFO: Merge_folder creation completed."

# Batch 3: Create Folderify test files
echo "INFO: Creating Folderify test files..."
for NUM in {01..05}; do
    touch "$TARGET_DIR/Folderify_$NUM"
    echo "INFO: Created file Folderify_$NUM"
done

echo "INFO: File creation completed."