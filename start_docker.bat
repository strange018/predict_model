@echo off
echo Building and starting Docker Compose services...
docker-compose build --no-cache
docker-compose up -d
echo Services started. Backend should be available on http://localhost:5000
