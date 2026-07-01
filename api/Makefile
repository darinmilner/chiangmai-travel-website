.PHONY: build run watch-css dev clean

# Run Go application
run:
	go run cmd/server/main.go

# Development with CSS watching
dev:
	@echo "Starting development server..."
	@make watch-css & make run

# Build Docker image
docker-build:
	docker build -t chiang-mai-business .

# Run Docker container
docker-run:
	docker run -p 8080:8080 chiang-mai-business

# Clean build artifacts
clean:
	rm -f static/css/styles.css
	rm -f chiang-mai-business
	go clean

# Install dependencies
deps:
	go mod download
	npm install