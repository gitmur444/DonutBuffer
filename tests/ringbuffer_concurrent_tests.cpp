#include <gtest/gtest.h>
#include <atomic>
#include <thread>
#include <vector>
#include <chrono>
#include <numeric>
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

// =============================================================================
// МНОГОПОТОЧНЫЕ ТЕСТЫ ДЛЯ MutexRingBuffer
// =============================================================================
// Проверяют thread safety и корректность работы в многопоточной среде
// с использованием мьютексов и condition variables
// =============================================================================

class MutexRingBufferConcurrentTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    void TearDown() override {
        stop_flag.store(true);  // Гарантируем остановку всех потоков
    }
    
    std::atomic<bool> stop_flag{false};
};

// СЦЕНАРИЙ: Single Producer Single Consumer (SPSC) с мьютексами
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Thread safety между одним производителем и одним потребителем
// 2. Отсутствие race conditions в критических секциях
// 3. Корректность работы condition variables при блокировках
// 4. Сохранение FIFO порядка при многопоточном доступе
// 5. Синхронизация завершения работы потоков
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Все элементы переданы в правильном порядке без потерь
TEST_F(MutexRingBufferConcurrentTest, SingleProducerSingleConsumer) {
    const size_t buffer_size = 100;   // Достаточно большой буфер для избежания частых блокировок
    const size_t num_items = 10000;   // Значительный объем данных для stress testing
    MutexRingBuffer rb(buffer_size);
    
    // Atomic счетчики для thread-safe мониторинга прогресса
    std::atomic<size_t> produced_count{0};
    std::atomic<size_t> consumed_count{0};
    std::vector<int> consumed_values;  // Для проверки корректности данных
    std::mutex consumed_mutex;         // Защита общего вектора
    
    // Producer thread
    std::thread producer([&]() {
        for (size_t i = 0; i < num_items; ++i) {
            while (!rb.produce(static_cast<int>(i), 0, stop_flag) && !stop_flag.load()) {
                std::this_thread::yield();
            }
            if (stop_flag.load()) break;
            produced_count.fetch_add(1);
        }
    });
    
    // Consumer thread
    std::thread consumer([&]() {
        int value;
        while (consumed_count.load() < num_items && !stop_flag.load()) {
            if (rb.consume(value, 0, stop_flag)) {
                {
                    std::lock_guard<std::mutex> lock(consumed_mutex);
                    consumed_values.push_back(value);
                }
                consumed_count.fetch_add(1);
            } else {
                std::this_thread::yield();
            }
        }
    });
    
    producer.join();
    consumer.join();
    
    EXPECT_EQ(produced_count.load(), num_items);
    EXPECT_EQ(consumed_count.load(), num_items);
    EXPECT_EQ(consumed_values.size(), num_items);
    
    // Check that all values were consumed in order
    for (size_t i = 0; i < consumed_values.size(); ++i) {
        EXPECT_EQ(consumed_values[i], static_cast<int>(i));
    }
}

TEST_F(MutexRingBufferConcurrentTest, MultipleProducersMultipleConsumers) {
    const size_t buffer_size = 100;
    const size_t num_producers = 4;
    const size_t num_consumers = 3;
    const size_t items_per_producer = 1000;
    const size_t total_items = num_producers * items_per_producer;
    
    MutexRingBuffer rb(buffer_size);
    
    std::atomic<size_t> produced_count{0};
    std::atomic<size_t> consumed_count{0};
    std::vector<int> all_consumed_values;
    std::mutex consumed_mutex;
    
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    
    // Create producer threads
    for (size_t p = 0; p < num_producers; ++p) {
        producers.emplace_back([&, p]() {
            for (size_t i = 0; i < items_per_producer; ++i) {
                int value = static_cast<int>(p * items_per_producer + i);
                while (!rb.produce(value, static_cast<int>(p), stop_flag) && !stop_flag.load()) {
                    std::this_thread::yield();
                }
                if (stop_flag.load()) break;
                produced_count.fetch_add(1);
            }
        });
    }
    
    // Create consumer threads
    for (size_t c = 0; c < num_consumers; ++c) {
        consumers.emplace_back([&, c]() {
            int value;
            while (consumed_count.load() < total_items && !stop_flag.load()) {
                if (rb.consume(value, static_cast<int>(c), stop_flag)) {
                    {
                        std::lock_guard<std::mutex> lock(consumed_mutex);
                        all_consumed_values.push_back(value);
                    }
                    consumed_count.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Wait for all threads to complete
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    EXPECT_EQ(produced_count.load(), total_items);
    EXPECT_EQ(consumed_count.load(), total_items);
    EXPECT_EQ(all_consumed_values.size(), total_items);
    
    // Sort and verify all expected values are present
    std::sort(all_consumed_values.begin(), all_consumed_values.end());
    for (size_t i = 0; i < total_items; ++i) {
        EXPECT_EQ(all_consumed_values[i], static_cast<int>(i));
    }
}

// Concurrent tests for LockFreeRingBuffer
class LockFreeRingBufferConcurrentTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    void TearDown() override {
        stop_flag.store(true);
    }
    
    std::atomic<bool> stop_flag{false};
};

TEST_F(LockFreeRingBufferConcurrentTest, SingleProducerSingleConsumer) {
    const size_t buffer_size = 100;
    const size_t num_items = 10000;
    LockFreeRingBuffer rb(buffer_size);
    
    std::atomic<size_t> produced_count{0};
    std::atomic<size_t> consumed_count{0};
    std::vector<int> consumed_values;
    std::mutex consumed_mutex;
    
    // Producer thread
    std::thread producer([&]() {
        for (size_t i = 0; i < num_items; ++i) {
            while (!rb.produce(static_cast<int>(i), 0, stop_flag) && !stop_flag.load()) {
                std::this_thread::yield();
            }
            if (stop_flag.load()) break;
            produced_count.fetch_add(1);
        }
    });
    
    // Consumer thread
    std::thread consumer([&]() {
        int value;
        while (consumed_count.load() < num_items && !stop_flag.load()) {
            if (rb.consume(value, 0, stop_flag)) {
                {
                    std::lock_guard<std::mutex> lock(consumed_mutex);
                    consumed_values.push_back(value);
                }
                consumed_count.fetch_add(1);
            } else {
                std::this_thread::yield();
            }
        }
    });
    
    producer.join();
    consumer.join();
    
    EXPECT_EQ(produced_count.load(), num_items);
    EXPECT_EQ(consumed_count.load(), num_items);
    EXPECT_EQ(consumed_values.size(), num_items);
    
    // Check that all values were consumed in order
    for (size_t i = 0; i < consumed_values.size(); ++i) {
        EXPECT_EQ(consumed_values[i], static_cast<int>(i));
    }
}

TEST_F(LockFreeRingBufferConcurrentTest, MultipleProducersMultipleConsumers) {
    const size_t buffer_size = 100;
    const size_t num_producers = 4;
    const size_t num_consumers = 3;
    const size_t items_per_producer = 1000;
    const size_t total_items = num_producers * items_per_producer;
    
    LockFreeRingBuffer rb(buffer_size);
    
    std::atomic<size_t> produced_count{0};
    std::atomic<size_t> consumed_count{0};
    std::vector<int> all_consumed_values;
    std::mutex consumed_mutex;
    
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    
    // Create producer threads
    for (size_t p = 0; p < num_producers; ++p) {
        producers.emplace_back([&, p]() {
            for (size_t i = 0; i < items_per_producer; ++i) {
                int value = static_cast<int>(p * items_per_producer + i);
                while (!rb.produce(value, static_cast<int>(p), stop_flag) && !stop_flag.load()) {
                    std::this_thread::yield();
                }
                if (stop_flag.load()) break;
                produced_count.fetch_add(1);
            }
        });
    }
    
    // Create consumer threads
    for (size_t c = 0; c < num_consumers; ++c) {
        consumers.emplace_back([&, c]() {
            int value;
            while (consumed_count.load() < total_items && !stop_flag.load()) {
                if (rb.consume(value, static_cast<int>(c), stop_flag)) {
                    {
                        std::lock_guard<std::mutex> lock(consumed_mutex);
                        all_consumed_values.push_back(value);
                    }
                    consumed_count.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Wait for all threads to complete
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    EXPECT_EQ(produced_count.load(), total_items);
    EXPECT_EQ(consumed_count.load(), total_items);
    EXPECT_EQ(all_consumed_values.size(), total_items);
    
    // Sort and verify all expected values are present
    std::sort(all_consumed_values.begin(), all_consumed_values.end());
    for (size_t i = 0; i < total_items; ++i) {
        EXPECT_EQ(all_consumed_values[i], static_cast<int>(i));
    }
}

// Stress test that applies to both implementations
template<typename RingBufferType>
class RingBufferStressTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    void TearDown() override {
        stop_flag.store(true);
    }
    
    std::atomic<bool> stop_flag{false};
};

typedef ::testing::Types<MutexRingBuffer, LockFreeRingBuffer> RingBufferTypes;
TYPED_TEST_SUITE(RingBufferStressTest, RingBufferTypes);

TYPED_TEST(RingBufferStressTest, HighContentionStressTest) {
    const size_t buffer_size = 16;  // Small buffer for high contention
    const size_t num_threads = std::thread::hardware_concurrency();
    const size_t operations_per_thread = 5000;
    const auto test_duration = std::chrono::seconds(5);
    
    TypeParam rb(buffer_size);
    std::atomic<size_t> total_produced{0};
    std::atomic<size_t> total_consumed{0};
    
    auto start_time = std::chrono::high_resolution_clock::now();
    std::vector<std::thread> threads;
    
    // Create threads that both produce and consume
    for (size_t i = 0; i < num_threads; ++i) {
        threads.emplace_back([&, i]() {
            size_t local_produced = 0;
            size_t local_consumed = 0;
            int value;
            
            while (std::chrono::high_resolution_clock::now() - start_time < test_duration && 
                   !this->stop_flag.load()) {
                
                // Try to produce
                if (rb.produce(static_cast<int>(i * 1000000 + local_produced), 
                              static_cast<int>(i), this->stop_flag)) {
                    local_produced++;
                }
                
                // Try to consume
                if (rb.consume(value, static_cast<int>(i), this->stop_flag)) {
                    local_consumed++;
                }
                
                if (local_produced >= operations_per_thread && 
                    local_consumed >= operations_per_thread) {
                    break;
                }
            }
            
            total_produced.fetch_add(local_produced);
            total_consumed.fetch_add(local_consumed);
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    // The test should complete without deadlocks or crashes
    EXPECT_GT(total_produced.load(), 0u);
    EXPECT_GT(total_consumed.load(), 0u);
    
    // In a stress test, we might not consume everything due to timing,
    // but the difference shouldn't be too large
    auto diff = std::abs(static_cast<long>(total_produced.load()) - 
                        static_cast<long>(total_consumed.load()));
    EXPECT_LE(diff, static_cast<long>(buffer_size));
}