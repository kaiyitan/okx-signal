#!/bin/bash
set -e

echo "=== Pulling latest code ==="
git pull

echo "=== Building and starting services ==="
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

echo "=== Status ==="
docker-compose -f docker-compose.prod.yml ps

echo "=== Done. API is running on http://$(curl -s ifconfig.me) ==="
