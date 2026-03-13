#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DAYS=${1:-7}

echo "=== RSS Article Collector ==="
echo "Collecting articles from last $DAYS days..."
python3 collector.py --days "$DAYS"

echo ""
echo "Filtering articles..."
python3 filter.py

echo ""
echo "Done! Articles are ready in db/articles.db"
