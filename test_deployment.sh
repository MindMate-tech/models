#!/bin/bash

# Test MindMate API Deployment
# Usage: ./test_deployment.sh https://your-render-url.onrender.com

API_URL="${1:-https://mindmate-cognitive-api.onrender.com}"

echo "Testing MindMate API at: $API_URL"
echo "=================================="

# Test 1: Health check
echo -e "\n1. Testing /health endpoint..."
curl -s "$API_URL/health" | jq .

# Test 2: Root endpoint
echo -e "\n2. Testing / endpoint..."
curl -s "$API_URL/" | jq .

# Test 3: Cache stats
echo -e "\n3. Testing /cache/stats endpoint..."
curl -s "$API_URL/cache/stats" | jq .

echo -e "\n✅ Deployment test complete!"
