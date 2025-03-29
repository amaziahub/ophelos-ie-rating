.PHONY: all

IMAGE_NAME ?= py-service-skeleton

test:
	@echo "Running tests..."
	pytest

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

run:
	@echo "Starting the application..."
	uvicorn service.app:app --reload --host 0.0.0.0 --port 8080

docker-build:
	@echo "Building Docker image: $(IMAGE_NAME)..."
	docker build -t $(IMAGE_NAME) .

docker-run:
	@echo "Running Docker container from image: $(IMAGE_NAME)..."
	docker run -p 8080:8080 $(IMAGE_NAME)
