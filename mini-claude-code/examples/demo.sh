#!/bin/bash
# Demo script for mini-claude-code Docker environment
# This script demonstrates multi-step reasoning, error correction, and state transitions

set -e

echo "========================================"
echo "  mini-claude-code Docker Quickstart"
echo "========================================"
echo ""

# Check environment
echo "[1/5] Checking environment..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "  ⚠ ANTHROPIC_API_KEY not set"
else
    echo "  ✓ ANTHROPIC_API_KEY is set"
fi

if [ -n "$MOCK_API_URL" ]; then
    echo "  ✓ MOCK_API_URL: $MOCK_API_URL"
fi

echo ""

# Test mock API endpoints
echo "[2/5] Testing Mock API..."
echo ""

echo "  → GET /api/health"
curl -s http://localhost:8080/api/health | python3 -m json.tool 2>/dev/null || echo "  ⚠ Mock API not running (run 'docker-compose up' first)"

echo ""
echo "  → GET /api/prices?symbols=BTC,ETH"
curl -s "http://localhost:8080/api/prices?symbols=BTC,ETH" | python3 -m json.tool 2>/dev/null || echo "  ⚠ Mock API not available"

echo ""
echo "  → GET /api/files?path=/data/sample.txt"
curl -s "http://localhost:8080/api/files?path=/data/sample.txt" | python3 -m json.tool 2>/dev/null || echo "  ⚠ Mock API not available"

echo ""

# Show workspace structure
echo "[3/5] Workspace structure:"
echo ""
find . -not -path '*/\.*' -not -path '*/workdir/*' | head -30 | sed 's|^\./|  |'

echo ""

# Show what agent can do
echo "[4/5] Agent capabilities demo:"
echo ""
echo "  Multi-step reasoning example:"
echo '    "Fetch BTC price, calculate portfolio value, save to file"'
echo ""
echo "  Error correction example:"
echo '    "Try to read /nonexistent.txt, on error fall back to /data/sample.txt"'
echo ""
echo "  State transitions:"
echo '    PENDING → PROCESSING → COMPLETED / ERROR'

echo ""
echo "[5/5] Ready to use!"
echo ""
echo "========================================"
echo "  Usage:"
echo "    docker-compose up"
echo "    docker-compose exec agent python main.py"
echo "========================================"
