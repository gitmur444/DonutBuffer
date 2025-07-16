#include <gtest/gtest.h>
#include <atomic>
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

// MutexRingBuffer Basic Tests
class MutexRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

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

TEST_F(MutexRingBufferTest, CapacityManagement) {
    MutexRingBuffer rb(2);
    
    EXPECT_EQ(rb.get_capacity(), 2u);
    EXPECT_EQ(rb.get_count(), 0u);
    
    // Fill to capacity
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
    
    // Should not be able to produce more
    EXPECT_FALSE(rb.produce(3, 0, stop_flag));
}

TEST_F(MutexRingBufferTest, EmptyBufferConsume) {
    MutexRingBuffer rb(2);
    int value = 0;
    
    // Should not be able to consume from empty buffer
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

TEST_F(MutexRingBufferTest, CircularOperation) {
    MutexRingBuffer rb(2);
    int value = 0;
    
    // Fill and empty multiple times
    for (int i = 0; i < 5; ++i) {
        EXPECT_TRUE(rb.produce(i * 10, 0, stop_flag));
        EXPECT_TRUE(rb.produce(i * 10 + 1, 0, stop_flag));
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10);
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10 + 1);
    }
}

// LockFreeRingBuffer Basic Tests
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

TEST_F(LockFreeRingBufferTest, CapacityManagement) {
    LockFreeRingBuffer rb(2);
    
    EXPECT_EQ(rb.get_capacity(), 2u);
    EXPECT_EQ(rb.get_count(), 0u);
    
    // Fill to capacity
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);
    
    // Should not be able to produce more
    EXPECT_FALSE(rb.produce(3, 0, stop_flag));
}

TEST_F(LockFreeRingBufferTest, EmptyBufferConsume) {
    LockFreeRingBuffer rb(2);
    int value = 0;
    
    // Should not be able to consume from empty buffer
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

TEST_F(LockFreeRingBufferTest, CircularOperation) {
    LockFreeRingBuffer rb(2);
    int value = 0;
    
    // Fill and empty multiple times
    for (int i = 0; i < 5; ++i) {
        EXPECT_TRUE(rb.produce(i * 10, 0, stop_flag));
        EXPECT_TRUE(rb.produce(i * 10 + 1, 0, stop_flag));
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10);
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10 + 1);
    }
}

// Tests that apply to both implementations
template<typename RingBufferType>
class RingBufferGenericTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

typedef ::testing::Types<MutexRingBuffer, LockFreeRingBuffer> RingBufferTypes;
TYPED_TEST_SUITE(RingBufferGenericTest, RingBufferTypes);

TYPED_TEST(RingBufferGenericTest, StopFlagRespected) {
    TypeParam rb(10);
    this->stop_flag.store(true);
    
    int value = 0;
    EXPECT_FALSE(rb.produce(1, 0, this->stop_flag));
    EXPECT_FALSE(rb.consume(value, 0, this->stop_flag));
}
