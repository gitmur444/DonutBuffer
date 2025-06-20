export module ringbuffer.mutex_ring_buffer_adapter;

#include "ringbuffer/abstract_ring_buffer.h"
#include <mutex>
#include <queue>

export class MutexRingBufferAdapter : public AbstractRingBuffer {
public:
    MutexRingBufferAdapter(size_t capacity);
    void push(int value) override;
    bool pop(int& value) override;
    size_t size() const override;
    size_t capacity() const override;
private:
    std::queue<int> buffer;
    size_t max_capacity;
    mutable std::mutex mtx;
};
