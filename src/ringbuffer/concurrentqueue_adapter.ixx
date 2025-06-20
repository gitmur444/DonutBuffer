export module ringbuffer.concurrentqueue_adapter;

#include "ringbuffer/abstract_ring_buffer.h"
#include <queue>
#include <mutex>

export class ConcurrentQueueAdapter : public AbstractRingBuffer {
public:
    ConcurrentQueueAdapter(size_t capacity);
    void push(int value) override;
    bool pop(int& value) override;
    size_t size() const override;
    size_t capacity() const override;
private:
    std::queue<int> buffer;
    size_t max_capacity;
    mutable std::mutex mtx;
};
