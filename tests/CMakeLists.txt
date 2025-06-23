add_executable(ringbuffer_tests
    ringbuffer_tests.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/mutex_ring_buffer.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../src/ringbuffer/lockfree_ring_buffer.cpp
)

# Include directories for ring buffer headers
# ${PROJECT_SOURCE_DIR} is root; but we are in tests

# CMake's current directory is tests; we need to include src

target_include_directories(ringbuffer_tests PRIVATE
    ${PROJECT_SOURCE_DIR}/src
)

target_link_libraries(ringbuffer_tests PRIVATE Threads::Threads)

add_test(NAME RingBufferTests COMMAND ringbuffer_tests)
