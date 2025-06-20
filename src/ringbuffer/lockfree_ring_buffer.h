#pragma once
#include <vector>
#include <atomic>
#include <cstddef>

class LockFreeRingBuffer {
public:
    LockFreeRingBuffer(size_t capacity);
    bool produce(int item, int producer_id, const std::atomic<bool>& stop_flag);
    bool consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag);
    size_t get_count();
    size_t get_capacity() const;
    void notify_all_on_stop() {}
private:
    struct Slot {
        std::atomic<size_t> sequence;
        int value;
    };
    size_t capacity;
    std::vector<Slot> buffer;
    std::atomic<size_t> head;
    std::atomic<size_t> tail;
};
