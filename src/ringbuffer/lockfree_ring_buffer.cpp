#include "lockfree_ring_buffer.h"
#include <atomic>
#include <thread>

LockFreeRingBuffer::LockFreeRingBuffer(size_t capacity)
    : capacity(capacity), buffer(capacity), head(0), tail(0) {
    for (size_t i = 0; i < capacity; ++i) {
        buffer[i].sequence.store(i, std::memory_order_relaxed);
    }
}

bool LockFreeRingBuffer::produce(int item, int /*producer_id*/, const std::atomic<bool>& stop_flag) {
    size_t pos;
    Slot* slot;
    while (!stop_flag) {
        size_t cur_tail = tail.load(std::memory_order_relaxed);
        pos = cur_tail % capacity;
        slot = &buffer[pos];
        size_t seq = slot->sequence.load(std::memory_order_acquire);
        intptr_t dif = (intptr_t)seq - (intptr_t)cur_tail;
        if (dif == 0) {
            if (tail.compare_exchange_weak(cur_tail, cur_tail + 1)) {
                slot->value = item;
                slot->sequence.store(cur_tail + 1, std::memory_order_release);
                return true;
            }
        } else if (dif < 0) {
            std::this_thread::yield();
            return false;
        } else {
            std::this_thread::yield();
        }
    }
    return false;
}

bool LockFreeRingBuffer::consume(int& item, int /*consumer_id*/, const std::atomic<bool>& stop_flag) {
    size_t pos;
    Slot* slot;
    while (!stop_flag) {
        size_t cur_head = head.load(std::memory_order_relaxed);
        pos = cur_head % capacity;
        slot = &buffer[pos];
        size_t seq = slot->sequence.load(std::memory_order_acquire);
        intptr_t dif = (intptr_t)seq - (intptr_t)(cur_head + 1);
        if (dif == 0) {
            if (head.compare_exchange_weak(cur_head, cur_head + 1)) {
                item = slot->value;
                slot->sequence.store(cur_head + capacity, std::memory_order_release);
                return true;
            }
        } else if (dif < 0) {
            std::this_thread::yield();
            return false;
        } else {
            std::this_thread::yield();
        }
    }
    return false;
}

size_t LockFreeRingBuffer::get_count() {
    size_t cur_tail = tail.load(std::memory_order_relaxed);
    size_t cur_head = head.load(std::memory_order_relaxed);
    return cur_tail >= cur_head ? cur_tail - cur_head : 0;
}

size_t LockFreeRingBuffer::get_capacity() const {
    return capacity;
}
