export module ringbuffer.lockfree_ring_buffer_adapter;

#include "ringbuffer/abstract_ring_buffer.h"
#include <atomic>
#include <vector>

export class LockFreeRingBufferAdapter : public AbstractRingBuffer {
public:
    LockFreeRingBufferAdapter(size_t capacity);
    void push(int value) override;
    bool pop(int& value) override;
    size_t size() const override;
    size_t capacity() const override;
private:
    std::vector<int> buffer;
    std::atomic<size_t> head;
    std::atomic<size_t> tail;
    size_t max_capacity;
};
