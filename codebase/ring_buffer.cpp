#include "../src/ringbuffer/mutex_ring_buffer.h"
#include <atomic>
#include <iostream>

// Simple demonstration program using the existing MutexRingBuffer
int main() {
    MutexRingBuffer rb(4);
    std::atomic<bool> stop{false};

    // Produce a couple of items
    rb.produce(1, 0, stop);
    rb.produce(2, 0, stop);

    // Consume and print the items
    int value = 0;
    rb.consume(value, 0, stop);
    std::cout << "First item: " << value << "\n";
    rb.consume(value, 0, stop);
    std::cout << "Second item: " << value << "\n";

    return 0;
}
