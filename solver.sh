#!/usr/bin/env bash

INPUT_DIR="$1"

if [ -z "$INPUT_DIR" ]; then
  echo "Usage: $0 <input_folder>"
  exit 1
fi

for file in "$INPUT_DIR"/*; do
  for solver in primal dual ip; do
    echo "Running $file with solver=$solver"
    python -m lp_solver -i "$file" -s "$solver"
    echo
  done
done
