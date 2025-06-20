#pragma once
#include <cstddef>
#include <atomic>

class AbstractRingBuffer {
public:
    virtual ~AbstractRingBuffer() = default;
    virtual bool produce(int item, int producer_id, const std::atomic<bool>& stop_flag) = 0;
    virtual bool consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag) = 0;
    virtual size_t get_count() = 0;
    virtual size_t get_capacity() const = 0;
    virtual void notify_all_on_stop() = 0;
};
