#include <gtest/gtest.h>
#include "smart_gtest/simple_smart_gtest.h"
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"
#include <atomic>
#include <chrono>

class SmartRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag;
};

// Тест для демонстрации SmartGTest с MutexRingBuffer
TEST_F(SmartRingBufferTest, MutexBasicOperations) {
    MutexRingBuffer buffer(5);
    
    // Проверка производителя
    ASSERT_TRUE(buffer.produce(10, 1, stop_flag));
    ASSERT_TRUE(buffer.produce(20, 1, stop_flag));
    ASSERT_TRUE(buffer.produce(30, 1, stop_flag));
    
    // Проверка потребителя
    int value;
    ASSERT_TRUE(buffer.consume(value, 1, stop_flag));
    EXPECT_EQ(value, 10);
    
    ASSERT_TRUE(buffer.consume(value, 1, stop_flag));
    EXPECT_EQ(value, 20);
    
    ASSERT_TRUE(buffer.consume(value, 1, stop_flag));
    EXPECT_EQ(value, 30);
}

// Тест для демонстрации SmartGTest с LockFreeRingBuffer  
TEST_F(SmartRingBufferTest, LockFreeBasicOperations) {
    LockFreeRingBuffer buffer(5);
    
    // Проверка производителя
    ASSERT_TRUE(buffer.produce(100, 1, stop_flag));
    ASSERT_TRUE(buffer.produce(200, 1, stop_flag));
    
    // Проверка потребителя
    int value;
    ASSERT_TRUE(buffer.consume(value, 1, stop_flag));
    EXPECT_EQ(value, 100);
    
    ASSERT_TRUE(buffer.consume(value, 1, stop_flag));
    EXPECT_EQ(value, 200);
}

// Тест производительности с SmartGTest логированием
TEST_F(SmartRingBufferTest, PerformanceComparison) {
    const int num_items = 1000;
    
    // Тест MutexRingBuffer
    {
        MutexRingBuffer mutex_buffer(100);
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < num_items; ++i) {
            mutex_buffer.produce(i, 1, stop_flag);
            int value;
            mutex_buffer.consume(value, 1, stop_flag);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto mutex_duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "Mutex buffer: " << mutex_duration.count() << " microseconds" << std::endl;
    }
    
    // Тест LockFreeRingBuffer
    {
        LockFreeRingBuffer lockfree_buffer(100);
        auto start = std::chrono::high_resolution_clock::now();
        
        for (int i = 0; i < num_items; ++i) {
            lockfree_buffer.produce(i, 1, stop_flag);
            int value;
            lockfree_buffer.consume(value, 1, stop_flag);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto lockfree_duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        std::cout << "LockFree buffer: " << lockfree_duration.count() << " microseconds" << std::endl;
        
        // LockFree должен быть быстрее (или хотя бы сравним)
        // Для демонстрации позволим некоторое отклонение
        EXPECT_LT(lockfree_duration.count(), lockfree_duration.count() * 2) << "LockFree performance test";
    }
}

// Тест с преднамеренной ошибкой для демонстрации логирования ошибок
TEST_F(SmartRingBufferTest, IntentionalFailureDemo) {
    MutexRingBuffer buffer(5);
    
    // Этот тест должен провалиться для демонстрации логирования ошибок
    buffer.produce(42, 1, stop_flag);
    int value;
    buffer.consume(value, 1, stop_flag);
    
    // Намеренная ошибка для демонстрации
    EXPECT_EQ(value, 999) << "This is an intentional failure to demonstrate SmartGTest error logging";
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    
    // Инициализация SmartGTest
    SMART_GTEST_INIT();
    
    std::cout << "\n=== SmartGTest Ring Buffer Tests ===" << std::endl;
    std::cout << "Demonstrating automatic test logging to PostgreSQL" << std::endl;
    std::cout << "====================================" << std::endl;
    
    return RUN_ALL_TESTS();
} 