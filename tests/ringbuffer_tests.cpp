#include <gtest/gtest.h>
#include <atomic>
#include <cassert>
#include <iostream>
#include <thread>
#include <vector>
#include <chrono>
#include "smart_gtest/simple_smart_gtest.h"
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

// =============================================================================
// БАЗОВЫЕ UNIT ТЕСТЫ ДЛЯ MutexRingBuffer
// =============================================================================

class MutexRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

// СЦЕНАРИЙ: Проверка базового цикла производства и потребления
TEST_F(MutexRingBufferTest, BasicProduceConsume) {
    MutexRingBuffer rb(2);
    
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
    
    int value = 0;
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 1);
    
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 2);
    EXPECT_EQ(rb.get_count(), 0u);
}

// СЦЕНАРИЙ: Проверка поведения при чтении из пустого буфера
TEST_F(MutexRingBufferTest, EmptyBufferConsume) {
    MutexRingBuffer rb(2);
    int value = 0;
    
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

// СЦЕНАРИЙ: Проверка циклических операций
TEST_F(MutexRingBufferTest, CircularOperation) {
    MutexRingBuffer rb(2);
    int value = 0;
    
    // Многократные циклы заполнения/освобождения
    for (int cycle = 0; cycle < 10; ++cycle) {
        // Заполняем буфер
        EXPECT_TRUE(rb.produce(cycle * 10 + 1, 0, stop_flag));
        EXPECT_TRUE(rb.produce(cycle * 10 + 2, 0, stop_flag));
        
        // Освобождаем буфер
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, cycle * 10 + 1);
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, cycle * 10 + 2);
    }
}

// СЦЕНАРИЙ: Многопоточный тест производительности
TEST_F(MutexRingBufferTest, MultithreadedPerformance) {
    const int buffer_size = 16;
    const int num_items = 10000;
    const int num_producers = 2;
    const int num_consumers = 2;
    
    MutexRingBuffer rb(buffer_size);
    std::atomic<int> produced(0);
    std::atomic<int> consumed(0);
    
    std::vector<std::thread> producers, consumers;
    auto start = std::chrono::high_resolution_clock::now();
    
    // Производители
    for (int i = 0; i < num_producers; ++i) {
        producers.emplace_back([&, i]() {
            while (!stop_flag.load()) {
                int item = produced.fetch_add(1);
                if (item >= num_items) break;
                
                while (!rb.produce(item, i, stop_flag)) {
                    if (stop_flag.load()) return;
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Потребители
    for (int i = 0; i < num_consumers; ++i) {
        consumers.emplace_back([&, i]() {
            int item;
            while (!stop_flag.load()) {
                if (consumed.load() >= num_items) break;
                
                if (rb.consume(item, i, stop_flag)) {
                    consumed.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Ждем завершения
    while (consumed.load() < num_items) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    
    stop_flag = true;
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    auto end = std::chrono::high_resolution_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();
    
    EXPECT_EQ(consumed.load(), num_items);
    std::cout << "Mutex: " << num_items << " items in " << seconds 
              << " sec (" << (num_items / seconds) << " items/sec)" << std::endl;
}

// =============================================================================
// БАЗОВЫЕ UNIT ТЕСТЫ ДЛЯ LockFreeRingBuffer
// =============================================================================

class LockFreeRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

TEST_F(LockFreeRingBufferTest, BasicProduceConsume) {
    LockFreeRingBuffer rb(2);
    
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
    
    int value = 0;
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 1);
    
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 2);
    EXPECT_EQ(rb.get_count(), 0u);
}

TEST_F(LockFreeRingBufferTest, EmptyBufferConsume) {
    LockFreeRingBuffer rb(2);
    int value = 0;
    
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

TEST_F(LockFreeRingBufferTest, CircularOperation) {
    LockFreeRingBuffer rb(2);
    int value = 0;
    
    for (int cycle = 0; cycle < 10; ++cycle) {
        EXPECT_TRUE(rb.produce(cycle * 10 + 1, 0, stop_flag));
        EXPECT_TRUE(rb.produce(cycle * 10 + 2, 0, stop_flag));
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, cycle * 10 + 1);
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, cycle * 10 + 2);
    }
}

TEST_F(LockFreeRingBufferTest, MultithreadedPerformance) {
    const int buffer_size = 16;
    const int num_items = 10000;
    const int num_producers = 2;
    const int num_consumers = 2;
    
    LockFreeRingBuffer rb(buffer_size);
    std::atomic<int> produced(0);
    std::atomic<int> consumed(0);
    
    std::vector<std::thread> producers, consumers;
    auto start = std::chrono::high_resolution_clock::now();
    
    // Производители
    for (int i = 0; i < num_producers; ++i) {
        producers.emplace_back([&, i]() {
            while (!stop_flag.load()) {
                int item = produced.fetch_add(1);
                if (item >= num_items) break;
                
                while (!rb.produce(item, i, stop_flag)) {
                    if (stop_flag.load()) return;
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Потребители
    for (int i = 0; i < num_consumers; ++i) {
        consumers.emplace_back([&, i]() {
            int item;
            while (!stop_flag.load()) {
                if (consumed.load() >= num_items) break;
                
                if (rb.consume(item, i, stop_flag)) {
                    consumed.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Ждем завершения
    while (consumed.load() < num_items) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    
    stop_flag = true;
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    
    auto end = std::chrono::high_resolution_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();
    
    EXPECT_EQ(consumed.load(), num_items);
    std::cout << "LockFree: " << num_items << " items in " << seconds 
              << " sec (" << (num_items / seconds) << " items/sec)" << std::endl;
}

// =============================================================================
// ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
// =============================================================================

TEST_F(MutexRingBufferTest, BufferFull) {
    MutexRingBuffer rb(2);
    
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
    
    // Попытка добавить в полный буфер может блокироваться или возвращать false
    // В зависимости от реализации
}

TEST_F(LockFreeRingBufferTest, BufferFull) {
    LockFreeRingBuffer rb(2);
    
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
}

// =============================================================================
// СРАВНИТЕЛЬНЫЕ ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
// =============================================================================

class PerformanceComparisonTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
    
    struct PerformanceResult {
        double items_per_sec;
        double duration_sec;
        int items_processed;
    };
    
    PerformanceResult test_performance(auto& buffer, int num_items, int producers, int consumers) {
        std::atomic<int> produced(0);
        std::atomic<int> consumed(0);
        
        std::vector<std::thread> producer_threads, consumer_threads;
        auto start = std::chrono::high_resolution_clock::now();
        
        // Производители
        for (int i = 0; i < producers; ++i) {
            producer_threads.emplace_back([&, i]() {
                while (!stop_flag.load()) {
                    int item = produced.fetch_add(1);
                    if (item >= num_items) break;
                    
                    while (!buffer.produce(item, i, stop_flag)) {
                        if (stop_flag.load()) return;
                        std::this_thread::yield();
                    }
                }
            });
        }
        
        // Потребители
        for (int i = 0; i < consumers; ++i) {
            consumer_threads.emplace_back([&, i]() {
                int item;
                while (!stop_flag.load()) {
                    if (consumed.load() >= num_items) break;
                    
                    if (buffer.consume(item, i, stop_flag)) {
                        consumed.fetch_add(1);
                    } else {
                        std::this_thread::yield();
                    }
                }
            });
        }
        
        // Ждем завершения
        while (consumed.load() < num_items) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        
        stop_flag = true;
        for (auto& t : producer_threads) t.join();
        for (auto& t : consumer_threads) t.join();
        
        auto end = std::chrono::high_resolution_clock::now();
        double duration = std::chrono::duration<double>(end - start).count();
        
        return {
            .items_per_sec = num_items / duration,
            .duration_sec = duration,
            .items_processed = consumed.load()
        };
    }
};

TEST_F(PerformanceComparisonTest, MutexVsLockFreeComparison) {
    const int buffer_size = 16;
    const int num_items = 50000;
    const int producers = 4;
    const int consumers = 4;
    
    // Тест Mutex буфера
    {
        MutexRingBuffer mutex_buffer(buffer_size);
        auto mutex_result = test_performance(mutex_buffer, num_items, producers, consumers);
        
        EXPECT_EQ(mutex_result.items_processed, num_items);
        EXPECT_GT(mutex_result.items_per_sec, 1000.0); // Минимум 1K items/sec
        
        std::cout << "Mutex Buffer: " << mutex_result.items_per_sec 
                  << " items/sec (" << mutex_result.duration_sec << " sec)" << std::endl;
    }
    
    stop_flag = false; // Сброс для следующего теста
    
    // Тест LockFree буфера
    {
        LockFreeRingBuffer lockfree_buffer(buffer_size);
        auto lockfree_result = test_performance(lockfree_buffer, num_items, producers, consumers);
        
        EXPECT_EQ(lockfree_result.items_processed, num_items);
        EXPECT_GT(lockfree_result.items_per_sec, 10000.0); // LockFree должен быть быстрее
        
        std::cout << "LockFree Buffer: " << lockfree_result.items_per_sec 
                  << " items/sec (" << lockfree_result.duration_sec << " sec)" << std::endl;
    }
}

// Custom main для SmartGTest
int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    
    // Инициализация SmartGTest
    SMART_GTEST_INIT();
    
    return RUN_ALL_TESTS();
}
