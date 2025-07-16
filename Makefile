# Simple proxy Makefile for building the project from the root directory

.PHONY: all build clean test test-unit test-e2e test-cli test-verbose help

all: build

# Build commands
build:
	@if [ ! -d build ]; then mkdir build; fi
	cd build && cmake .. -G "Unix Makefiles"
	cd build && make

build-with-tests:
	@if [ ! -d build ]; then mkdir build; fi
	cd build && cmake .. -G "Unix Makefiles"
	cd build && make

clean:
	cd build && make clean || true

# Test commands (using build for tests)
test: build-with-tests
	./run-tests.sh

test-unit: build-with-tests
	./run-tests.sh unit

test-e2e: build-with-tests
	./run-tests.sh e2e

test-cli: build-with-tests
	./run-tests.sh cli

test-verbose: build-with-tests
	./run-tests.sh all -v

# Quick commands using build directory directly
test-quick:
	@if [ -d build ]; then \
		cd build && ctest; \
	else \
		echo "❌ build directory not found. Run 'make build-with-tests' first."; \
	fi

test-quick-verbose:
	@if [ -d build ]; then \
		cd build && ctest -V; \
	else \
		echo "❌ build directory not found. Run 'make build-with-tests' first."; \
	fi

# Help
help:
	@echo "🎯 DonutBuffer Makefile Commands:"
	@echo ""
	@echo "Building:"
	@echo "  make build             - Build main project (basic version)"
	@echo "  make build-with-tests  - Build with all tests included"
	@echo ""
	@echo "Testing (comprehensive with scripts):"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run only unit tests"
	@echo "  make test-e2e     - Run only E2E tests"
	@echo "  make test-cli     - Run CLI performance tests"
	@echo "  make test-verbose - Run all tests with verbose output"
	@echo ""
	@echo "Testing (quick CTest):"
	@echo "  make test-quick          - Quick CTest run"
	@echo "  make test-quick-verbose  - Quick CTest run with verbose output"
	@echo ""
	@echo "Other:"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make help         - Show this help"
	@echo ""
	@echo "Direct script usage:"
	@echo "  ./run-tests.sh [command] [options]"
	@echo "  ./test [command] [options]"
