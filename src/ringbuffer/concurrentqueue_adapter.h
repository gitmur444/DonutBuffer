#pragma once
#include "ringbuffer/abstract_ring_buffer.h"
#include "../external/concurrentqueue/concurrentqueue.h" // moodycamel::ConcurrentQueue
#include <atomic>
#include <memory>

class ConcurrentQueueAdapter : public AbstractRingBuffer {
public:
    ConcurrentQueueAdapter(size_t capacity) : queue(capacity), max_capacity(capacity), count(0) {}
    bool produce(int item, int /*producer_id*/, const std::atomic<bool>& stop_flag) override {
        if (stop_flag) return false;
        // Capacity limit: concurrentqueue is non-blocking, so we count manually
        size_t expected;
        do {
            expected = count.load();
            if (expected >= max_capacity) return false;
        } while (!count.compare_exchange_weak(expected, expected + 1));
        bool ok = queue.enqueue(item);
        if (!ok) count.fetch_sub(1);
        return ok;
    }
    bool consume(int& item, int /*consumer_id*/, const std::atomic<bool>& stop_flag) override {
        if (stop_flag) return false;
        bool ok = queue.try_dequeue(item);
        if (ok) count.fetch_sub(1);
        return ok;
    }
    size_t get_count() override {
        return count.load();
    }
    size_t get_capacity() const override {
        return max_capacity;
    }
    void notify_all_on_stop() override {}
private:
    moodycamel::ConcurrentQueue<int> queue;
    const size_t max_capacity;
    std::atomic<size_t> count;
};
