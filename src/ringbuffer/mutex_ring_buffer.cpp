#include "mutex_ring_buffer.h"
#include <chrono>

MutexRingBuffer::MutexRingBuffer(size_t capacity) : capacity(capacity), buffer(capacity), head(0), tail(0), count(0) {}

bool MutexRingBuffer::produce(int item, int producer_id, const std::atomic<bool>& stop_flag) {
    std::unique_lock<std::mutex> lock(mutex);
    if (!cv_not_full.wait_for(lock, std::chrono::milliseconds(100), [&] { return count < capacity || stop_flag; })) {
        return !stop_flag;
    }
    if (stop_flag) {
        return false;
    }
    buffer[tail] = item;
    tail = (tail + 1) % capacity;
    count++;
    lock.unlock();
    cv_not_empty.notify_one();
    return true;
}

bool MutexRingBuffer::consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag) {
    std::unique_lock<std::mutex> lock(mutex);
    if (!cv_not_empty.wait_for(lock, std::chrono::milliseconds(100), [&] { return count > 0 || stop_flag; })) {
        return !stop_flag;
    }
    if (count == 0 && stop_flag) {
        return false;
    }
    if (count == 0) {
        item = 0;
        return true;
    }
    item = buffer[head];
    head = (head + 1) % capacity;
    count--;
    lock.unlock();
    cv_not_full.notify_one();
    return true;
}

size_t MutexRingBuffer::get_count() {
    return count.load();
}

size_t MutexRingBuffer::get_capacity() const {
    return capacity;
}

void MutexRingBuffer::notify_all_on_stop() {
    cv_not_full.notify_all();
    cv_not_empty.notify_all();
}
