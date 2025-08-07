# Simple proxy Makefile for building the project from the root directory

.PHONY: all build clean test test-unit test-e2e test-cli test-verbose all-tests help

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

# Smart GTest integrated tests - all tests with database logging
all-tests: build-with-tests
	@echo "🚀 Running ALL DonutBuffer tests with Smart GTest integration"
	@echo "============================================================="
	@echo "🧹 Clearing actual_tests table for fresh test run..."
	@if docker ps | grep -q smart_test_postgres; then \
		docker exec smart_test_postgres psql -U postgres -d smart_tests -c "SELECT clear_actual_tests();" > /dev/null 2>&1 && \
		echo "✅ actual_tests table cleared"; \
	else \
		echo "⚠️  PostgreSQL not running - tests will run without Smart GTest logging"; \
	fi
	@echo ""
	@echo "📋 Running Unit Tests..."
	@cd build/tests && set -a && source ../../tests/smart_gtest/.env && set +a && ./ringbuffer_tests
	@echo ""
	@echo "📋 Running Concurrent Tests..."
	@cd build/tests && set -a && source ../../tests/smart_gtest/.env && set +a && ./ringbuffer_concurrent_tests
	@echo ""
	@echo "📋 Running Performance Tests..."
	@cd build/tests && set -a && source ../../tests/smart_gtest/.env && set +a && ./ringbuffer_performance_tests
	@echo ""
	@echo "📋 Running E2E Tests..."
	@cd build/tests && ./e2e_buffer_tests
	@echo ""
	@echo "🎉 All tests completed!"
	@echo "📊 Checking Smart GTest results..."
	@if docker ps | grep -q smart_test_postgres; then \
		echo "Current test status in actual_tests:"; \
		docker exec smart_test_postgres psql -U postgres -d smart_tests -c "\
			SELECT \
				test_suite, \
				test_name, \
				status, \
				CASE WHEN status = 'PASSED' THEN '✅' WHEN status = 'FAILED' THEN '❌' ELSE '⏭️' END as icon, \
				execution_time_ms || 'ms' as time \
			FROM actual_tests ORDER BY test_suite, test_name;" 2>/dev/null || echo "No Smart GTest data available"; \
		echo ""; \
		echo "📈 Summary:"; \
		docker exec smart_test_postgres psql -U postgres -d smart_tests -c "\
			SELECT \
				total_tests || ' total, ' || \
				passed_tests || ' ✅ passed, ' || \
				failed_tests || ' ❌ failed' as summary \
			FROM actual_tests_summary;" 2>/dev/null || echo "Summary not available"; \
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
	@echo "Smart GTest Integration:"
	@echo "  make all-tests    - Run ALL tests with Smart GTest logging (clears actual_tests first)"
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
