#include "ring_buffer.h"
#include <chrono> // For std::chrono::milliseconds

RingBuffer::RingBuffer(size_t capacity) : capacity(capacity), buffer(capacity), head(0), tail(0), count(0) {}

bool RingBuffer::produce(int item, int producer_id, const std::atomic<bool>& stop_flag) {
    std::unique_lock<std::mutex> lock(mutex);
    if (!cv_not_full.wait_for(lock, std::chrono::milliseconds(100), [&] { return count < capacity || stop_flag; })) {
        // Timeout, useful if stop_flag is set while waiting
        return !stop_flag; // Continue if not stopping, else signal to stop producing
    }

    if (stop_flag) {
        return false; // Stop producing
    }

    buffer[tail] = item;
    tail = (tail + 1) % capacity;
    count++;
    lock.unlock();
    cv_not_empty.notify_one();
    return true;
}

bool RingBuffer::consume(int& item, int consumer_id, const std::atomic<bool>& stop_flag) {
    std::unique_lock<std::mutex> lock(mutex);
    if (!cv_not_empty.wait_for(lock, std::chrono::milliseconds(100), [&] { return count > 0 || stop_flag; })) {
         // Timeout
        return !stop_flag; // Continue if not stopping and buffer might get items, else signal to stop
    }

    if (count == 0 && stop_flag) {
        return false; // Stop consuming, buffer is empty
    }
    if (count == 0) { // Spurious wakeup or producers finished
        item = 0; // Ensure item is in a defined state, though not strictly necessary if not used
        return true; // Indicate still active, but no item consumed this round
    }

    item = buffer[head];
    head = (head + 1) % capacity;
    count--;
    lock.unlock();
    cv_not_full.notify_one();
    return true; // Item consumed
}

size_t RingBuffer::get_count() {
    std::lock_guard<std::mutex> lock(mutex);
    return count;
}

size_t RingBuffer::get_capacity() const {
    return capacity;
}

void RingBuffer::notify_all_on_stop() {
    cv_not_full.notify_all();
    cv_not_empty.notify_all();
}
