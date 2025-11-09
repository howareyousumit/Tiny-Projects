.PHONY: build run stop clean test logs shell help

# Variables
CONTAINER_NAME=json-formatter
IMAGE_NAME=json-formatter
PORT=8000

# Build the Docker image
build:
	@echo "Building Docker image..."
	@docker build -t $(IMAGE_NAME) .

# Run the container
run:
	@echo "Starting container..."
	@docker run -d --name $(CONTAINER_NAME) -p $(PORT):8000 $(IMAGE_NAME)
	@echo "Container started. Access the app at http://localhost:$(PORT)"

# Stop and remove the container
stop:
	@echo "Stopping container..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Container stopped and removed"

# Clean up the container and image
clean: stop
	@echo "Removing Docker image..."
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true
	@echo "Cleanup complete"

# Test the service
test:
	@echo "Testing the service..."
	@echo "1. Testing with valid JSON..."
	@curl -X POST "http://localhost:$(PORT)/api/format" \
		-H "Content-Type: application/json" \
		-d '{"text": "{\"name\":\"John\",\"age\":30,\"city\":\"New York\"}", "indent": 2}' \
		--output test_output.json
	@echo "\n2. Test output written to test_output.json"
	@echo "\n3. Service is running! Access the web interface at http://localhost:$(PORT)"

# Show logs
logs:
	@docker logs -f $(CONTAINER_NAME)

# Open a shell in the container
shell:
	@docker exec -it $(CONTAINER_NAME) /bin/bash

# Help
help:
	@echo "Available commands:"
	@echo "  make build    - Build the Docker image"
	@echo "  make run      - Run the container"
	@echo "  make stop     - Stop the container"
	@echo "  make logs     - View container logs"
	@echo "  make shell    - Open a shell in the container"
	@echo "  make clean    - Remove container and image"
	@echo "  make test     - Test the service with sample data"
	@echo "  make help     - Show this help message"