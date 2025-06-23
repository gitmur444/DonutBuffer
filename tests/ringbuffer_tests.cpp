#include <atomic>
#include <cassert>
#include <iostream>
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

void test_mutex_basic() {
    MutexRingBuffer rb(2);
    std::atomic<bool> stop(false);
    assert(rb.produce(1, 0, stop));
    assert(rb.produce(2, 0, stop));
    int v = 0;
    assert(rb.consume(v, 0, stop));
    assert(v == 1);
    assert(rb.consume(v, 0, stop));
    assert(v == 2);
}

void test_lockfree_basic() {
    LockFreeRingBuffer rb(2);
    std::atomic<bool> stop(false);
    assert(rb.produce(1, 0, stop));
    assert(rb.produce(2, 0, stop));
    int v = 0;
    assert(rb.consume(v, 0, stop));
    assert(v == 1);
    assert(rb.consume(v, 0, stop));
    assert(v == 2);
}

int main() {
    test_mutex_basic();
    test_lockfree_basic();
    std::cout << "All tests passed\n";
    return 0;
}
