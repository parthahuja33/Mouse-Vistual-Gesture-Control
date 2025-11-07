#!/bin/bash
# Virtual Mouse Launcher Script for Linux/macOS

set -e

echo ""
echo "========================================"
echo "  Virtual Mouse - Gesture Control"
echo "========================================"
echo ""

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

[ -d "venv" ] && source venv/bin/activate

# Parse command line arguments
SHOW_DEBUG=0
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --debug|--show-debug|-d)
            SHOW_DEBUG=1
            shift
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

echo "Starting Virtual Mouse..."
echo "Press Ctrl+C to exit"
echo ""
if [ $SHOW_DEBUG -eq 1 ]; then
    python3 -m src.main --show-debug --auto-start "${ARGS[@]}"
else
    python3 -m src.main --auto-start "${ARGS[@]}"
fi

echo ""
echo "Virtual Mouse stopped."

