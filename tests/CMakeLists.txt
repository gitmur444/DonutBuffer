# Basic ring buffer tests with GTest
add_executable(ringbuffer_tests
    ringbuffer_tests.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
)

target_link_libraries(ringbuffer_tests 
    PRIVATE 
    GTest::gtest_main
    Threads::Threads
)

# Advanced concurrent tests
add_executable(ringbuffer_concurrent_tests
    ringbuffer_concurrent_tests.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_concurrent_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
)

target_link_libraries(ringbuffer_concurrent_tests 
    PRIVATE 
    GTest::gtest_main
    Threads::Threads
)

# Performance comparison tests
add_executable(ringbuffer_performance_tests
    ringbuffer_performance_tests.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

target_include_directories(ringbuffer_performance_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
)

target_link_libraries(ringbuffer_performance_tests 
    PRIVATE 
    GTest::gtest_main
    Threads::Threads
)

# Register tests with CTest
add_test(NAME RingBufferBasicTests COMMAND ringbuffer_tests)
add_test(NAME RingBufferConcurrentTests COMMAND ringbuffer_concurrent_tests)
add_test(NAME RingBufferPerformanceTests COMMAND ringbuffer_performance_tests)

include(GoogleTest)
gtest_discover_tests(ringbuffer_tests)
gtest_discover_tests(ringbuffer_concurrent_tests)
gtest_discover_tests(ringbuffer_performance_tests)
