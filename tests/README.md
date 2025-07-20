# 🧪 DonutBuffer - Testing System Guide for AI Agents

## 📋 Overview

DonutBuffer uses a comprehensive testing system with **SmartGTest** - an intelligent testing framework that automatically logs test results to PostgreSQL database for analysis and monitoring.

## 🏗️ Test Architecture

### Core Components

1. **SmartGTest System** (`smart_gtest/simple_smart_gtest.h`)
   - Header-only PostgreSQL logging integration for GTest
   - Automatic test metadata capture (suite, name, status, timing, description, tags)
   - Real-time database logging with connection pooling

2. **Test Executables**
   - `ringbuffer_tests` - Unit tests for basic ring buffer functionality
   - `ringbuffer_concurrent_tests` - Multi-threaded concurrency tests  
   - `ringbuffer_performance_tests` - Performance benchmarks
   - `smart_ringbuffer_test` - SmartGTest demonstration
   - `e2e_buffer_tests` - End-to-end CLI tests

3. **Database Integration**
   - PostgreSQL backend for test result storage
   - Two-table architecture: historical + current state tracking
   - SQL functions for efficient test result management

## 📊 Database Schema

### Table: `test_results` (Historical)
```sql
CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    suite_name VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,           -- PASSED, FAILED, SKIPPED
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER DEFAULT 0,
    description TEXT,                      -- Test purpose/scenario
    tags VARCHAR(500),                     -- Comma-separated tags
    start_time TIMESTAMP,
    end_time TIMESTAMP
);
```

### Table: `actual_tests` (Current State)
```sql
CREATE TABLE actual_tests (
    id SERIAL PRIMARY KEY,
    suite_name VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER DEFAULT 0,
    description TEXT,
    tags VARCHAR(500),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    UNIQUE(suite_name, test_name)
);
```

### Key SQL Functions

- `clear_actual_tests()` - Clears current test state table
- `upsert_actual_test_v2()` - Updates/inserts current test results
- Automatic archival to `test_results` table

## 🚀 Running Tests

### Single Command (Recommended)
```bash
# From build/ directory
make all-tests
```

**What this does:**
1. Clears `actual_tests` table
2. Runs all test executables sequentially
3. Logs results to both database tables
4. Shows summary of test results

### Individual Test Execution
```bash
# From build/ directory
./tests/ringbuffer_tests              # Unit tests
./tests/ringbuffer_concurrent_tests   # Concurrency tests  
./tests/ringbuffer_performance_tests  # Performance tests
./tests/smart_ringbuffer_test         # SmartGTest demo
./tests/e2e_buffer_tests             # E2E tests
```

### Database Connection Setup
```bash
# Ensure PostgreSQL is running locally
brew services start postgresql

# Connection details (configured in simple_smart_gtest.h):
# Host: localhost
# Port: 5432  
# Database: test_results
# User: testuser
# Password: testpass
```

## 📈 Test Analysis Queries

### Current Test Status
```sql
SELECT suite_name, test_name, status, duration_ms, description 
FROM actual_tests 
ORDER BY suite_name, test_name;
```

### Performance Trending
```sql
SELECT suite_name, test_name, 
       AVG(duration_ms) as avg_duration,
       COUNT(*) as run_count
FROM test_results 
WHERE run_timestamp > NOW() - INTERVAL '1 day'
GROUP BY suite_name, test_name
ORDER BY avg_duration DESC;
```

### Failed Tests Investigation
```sql
SELECT * FROM test_results 
WHERE status = 'FAILED' 
ORDER BY run_timestamp DESC 
LIMIT 10;
```

## 🔍 Test Categories

### Unit Tests (`ringbuffer_tests`)
- **Basic Operations**: produce/consume, FIFO order
- **Boundary Conditions**: full buffer, empty buffer
- **Data Integrity**: sequence verification
- **Tags**: `unit`, `basic`, `boundary`

### Concurrency Tests (`ringbuffer_concurrent_tests`)  
- **Multi-producer/Consumer**: thread safety verification
- **Race Conditions**: lockfree vs mutex implementations
- **Stress Testing**: high contention scenarios
- **Tags**: `concurrent`, `multithreaded`, `stress`

### Performance Tests (`ringbuffer_performance_tests`)
- **Throughput Benchmarks**: operations per second
- **Latency Measurements**: operation timing
- **Scalability**: performance vs thread count
- **Tags**: `performance`, `benchmark`, `latency`

## 🤖 AI Agent Instructions

### For Test Discovery
1. Query `actual_tests` table to see current test landscape
2. Use `tags` field to filter by test categories
3. Check `description` field for test purpose understanding

### For Test Analysis
1. Compare performance metrics across runs using `test_results`
2. Identify failing patterns by test name/suite
3. Use timing data for performance regression detection

### For New Test Creation
1. Follow existing naming conventions: `SuiteName.TestName`
2. Add meaningful descriptions explaining test purpose
3. Use appropriate tags for categorization
4. Include SmartGTest header: `#include "smart_gtest/simple_smart_gtest.h"`

### Build Integration
- Tests are built automatically with main project
- CMake target `all-tests` runs complete test suite
- Individual test targets available for focused testing
- Database logging happens transparently during test execution

## 📝 Notes for AI Development

- **Test Discovery**: Always check `actual_tests` for current test inventory
- **Performance Analysis**: Use `test_results` historical data for trends
- **Failure Investigation**: Query by status and timestamp for recent issues
- **Test Metadata**: Leverage description and tags for intelligent test management
- **Database Connection**: System handles connection management automatically
- **Retry Logic**: Built-in timeout and retry for performance tests 