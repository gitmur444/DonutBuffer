# Basic ring buffer tests with GTest
add_executable(ringbuffer_tests
    ringbuffer_tests.cpp
    smart_gtest/simple_smart_gtest.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(ringbuffer_tests 
    PRIVATE 
    gtest
    Threads::Threads
)

# Advanced concurrent tests
add_executable(ringbuffer_concurrent_tests
    ringbuffer_concurrent_tests.cpp
    smart_gtest/simple_smart_gtest.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_concurrent_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(ringbuffer_concurrent_tests 
    PRIVATE 
    gtest
    Threads::Threads
)

# Performance comparison tests
add_executable(ringbuffer_performance_tests
    ringbuffer_performance_tests.cpp
    smart_gtest/simple_smart_gtest.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_performance_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(ringbuffer_performance_tests 
    PRIVATE 
    gtest
    Threads::Threads
)

# Smart RingBuffer tests with SmartGTest logging
add_executable(smart_ringbuffer_test
    smart_ringbuffer_test.cpp
    smart_gtest/simple_smart_gtest.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(smart_ringbuffer_test PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(smart_ringbuffer_test 
    PRIVATE 
    gtest
    Threads::Threads
)

# E2E тесты для CLI-версии
add_executable(e2e_buffer_tests
    e2e_buffer_tests.cpp
)

target_link_libraries(e2e_buffer_tests PRIVATE Threads::Threads)

# Register tests with CTest
add_test(NAME RingBufferBasicTests COMMAND ringbuffer_tests)
add_test(NAME RingBufferConcurrentTests COMMAND ringbuffer_concurrent_tests)
add_test(NAME RingBufferPerformanceTests COMMAND ringbuffer_performance_tests)

# Добавляем e2e тест, который запускает BufferRunner
add_test(NAME E2EBufferTests 
    COMMAND e2e_buffer_tests $<TARGET_FILE:BufferRunner>
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Убеждаемся, что BufferRunner собирается перед e2e тестами
add_dependencies(e2e_buffer_tests BufferRunner)

# Add smart_gtest subdirectory (optional)
# Temporarily disabled due to linking issues
# find_package(PostgreSQL QUIET)
# if(PostgreSQL_FOUND)
#     message(STATUS "PostgreSQL found - enabling smart_gtest")
#     add_subdirectory(smart_gtest)
# else()
#     message(STATUS "PostgreSQL not found - skipping smart_gtest (install with: brew install postgresql)")
# endif()

# All tests target with SmartGTest integration
add_custom_target(all-tests
    COMMAND echo "🚀 Starting SmartGTest full test run..."
    COMMAND psql -d testdb -c "SELECT clear_actual_tests\\(\\)\\;" || echo "Database not available, continuing without clearing..."
    COMMAND echo "📋 Running Unit Tests..."
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/ringbuffer_tests || true
    COMMAND echo "⚡ Running Concurrent Tests..."
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/ringbuffer_concurrent_tests || true
    COMMAND echo "🏃 Running Performance Tests..."
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/ringbuffer_performance_tests || true
    COMMAND echo "🔧 Running SmartGTest Demo..."
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/smart_ringbuffer_test || true
    COMMAND echo "🎯 Running E2E Tests..."
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/e2e_buffer_tests ${CMAKE_BINARY_DIR}/BufferRunner || true
    COMMAND echo "📊 SmartGTest Results Summary:"
    COMMAND psql -d testdb -c "SELECT test_suite, test_name, status, execution_time_ms FROM actual_tests ORDER BY test_suite, test_name\\;" || echo "Database not available for results summary"
    DEPENDS ringbuffer_tests ringbuffer_concurrent_tests ringbuffer_performance_tests smart_ringbuffer_test e2e_buffer_tests BufferRunner
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running all tests with SmartGTest logging"
)

include(GoogleTest)
gtest_discover_tests(ringbuffer_tests)
gtest_discover_tests(ringbuffer_concurrent_tests)
gtest_discover_tests(ringbuffer_performance_tests)
