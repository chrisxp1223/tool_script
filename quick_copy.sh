#!/bin/bash
# Quick SCP transfer script - Uses command line arguments

# Usage function
usage() {
    echo "Usage: $0 <Windows_IP> <Username> [Target_Path]"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100 myuser"
    echo "  $0 192.168.1.100 myuser /c/tmp"
    echo "  $0 192.168.1.100 myuser /mnt/c/tmp  # For WSL"
    echo ""
    echo "Will transfer the following files (if they exist):"
    echo "  - image-birmanplus.int.bin"
    echo "  - image-birmanplus.int.nda.bin"
    exit 1
}

# Check arguments
if [ $# -lt 2 ]; then
    usage
fi

WINDOWS_HOST="$1"
WINDOWS_USER="$2"
TARGET_DIR="${3:-C:/tmp/fw_image}"  # Default to C:\tmp on Windows

echo "=========================================="
echo "Quick SCP Transfer"
echo "=========================================="
echo "Target: ${WINDOWS_USER}@${WINDOWS_HOST}"
echo "Path: ${TARGET_DIR}"
echo ""

# File list
FILES=(
    "image-birmanplus.int.bin"
    "image-birmanplus.int.nda.bin"
)

# Collect existing files
EXISTING_FILES=()
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        EXISTING_FILES+=("$file")
        echo "✓ $file"
    fi
done

echo ""

if [ ${#EXISTING_FILES[@]} -eq 0 ]; then
    echo "Error: No files found"
    exit 1
fi

echo "Preparing to transfer ${#EXISTING_FILES[@]} file(s)..."
echo ""

# Test connection and create directory
echo "Testing connection and creating directory..."
echo "Target directory: ${TARGET_DIR}"
if ! ssh "${WINDOWS_USER}@${WINDOWS_HOST}" "powershell -Command \"New-Item -ItemType Directory -Path '${TARGET_DIR}' -Force | Out-Null\""; then
    echo ""
    echo "Error: Failed to create directory ${TARGET_DIR}"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Make sure Windows OpenSSH Server is installed and running"
    echo "  2. Verify you have permission to create ${TARGET_DIR}"
    echo "  3. Try a different path, e.g.: ./quick_copy.sh $WINDOWS_HOST $WINDOWS_USER C:/Users/$WINDOWS_USER/tmp"
    exit 1
fi

echo "Connection successful! Starting transfer..."
echo ""

# Transfer all files (in one go)
scp "${EXISTING_FILES[@]}" "${WINDOWS_USER}@${WINDOWS_HOST}:${TARGET_DIR}/"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Transfer Complete!"
    echo "=========================================="
    echo "Files transferred to: ${TARGET_DIR}"
else
    echo ""
    echo "=========================================="
    echo "✗ Transfer Failed"
    echo "=========================================="
    exit 1
fi
