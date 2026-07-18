#!/bin/bash
# Run everything locally

# 1. Run Go frontend
cd ../..api
go run main.go &

# 2. Run Lambda locally (if using SAM)
cd ../backend/lambda
python3 -m pytest tests/ -v

# 3. Test the full stack
curl http://localhost:8080

echo "✅ Local development environment running!"