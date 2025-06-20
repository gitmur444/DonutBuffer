#pragma once
#include <vector>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <cstddef>

class MutexRingBuffer {
public:
    MutexRingBuffer(size_t capacity);
    bool produce(int item, int producer_id, const std::atomic<bool>& stop_flag);
    bool consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag);
    size_t get_count();
    size_t get_capacity() const;
    void notify_all_on_stop();
private:
    size_t capacity;
    std::vector<int> buffer;
    size_t head;
    size_t tail;
    std::atomic<size_t> count;
    std::mutex mutex;
    std::condition_variable cv_not_full;
    std::condition_variable cv_not_empty;
};
