#pragma once
#include "lockfree_ring_buffer.h"
#include "ringbuffer/abstract_ring_buffer.h"
#include <memory>

class LockFreeRingBufferAdapter : public AbstractRingBuffer {
public:
    explicit LockFreeRingBufferAdapter(size_t capacity)
        : buffer(std::make_unique<LockFreeRingBuffer>(capacity)) {}
    bool produce(int item, int producer_id, const std::atomic<bool>& stop_flag) override {
        return buffer->produce(item, producer_id, stop_flag);
    }
    bool consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag) override {
        return buffer->consume(item, consumer_id, stop_flag);
    }
    size_t get_count() override {
        return buffer->get_count();
    }
    size_t get_capacity() const override {
        return buffer->get_capacity();
    }
    void notify_all_on_stop() override {
        buffer->notify_all_on_stop();
    }
private:
    std::unique_ptr<LockFreeRingBuffer> buffer;
};
