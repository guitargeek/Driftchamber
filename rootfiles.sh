#!/bin/bash

#############################################################################
# This script uses decode.py to convert the data archive with the binary data
# files to a directory with corresponding rootfiles.
#############################################################################

# Name of the data archive and target directory for rootfiles
ROOTFILES_DIR="rootfiles"
DATA_DIR="driftchamber-vp-data"
DATA_ARCHIVE="driftchamber-vp-data.tar.gz"
DECODE_SCRIPT="code/decode.py"

# Do nothing if the directory already exists for safety reasons
if [ -d "$ROOTFILES_DIR" ]; then
    echo "Directory $ROOTFILES_DIR already exists. Nothing will be done."
    exit
fi

# Unpack dara archive
echo "Unpacking $DATA_ARCHIVE..."
tar -xf $DATA_ARCHIVE
mv "$DATA_DIR" "$ROOTFILES_DIR"

# Convert to rootfiles
find "$ROOTFILES_DIR" -name '*.dat'  | while read line; do
    echo "Processing file $line"
    python "$DECODE_SCRIPT" "$line"
    rm "$line"
done
