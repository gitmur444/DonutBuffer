#include <gtest/gtest.h>
#include <atomic>
#include <thread>
#include <vector>
#include <chrono>
#include <numeric>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

struct PerformanceResult {
    std::chrono::nanoseconds duration;
    size_t operations_per_second;
    size_t total_operations;
    
    void print(const std::string& test_name) const {
        std::cout << test_name << ":\n";
        std::cout << "  Duration: " << duration.count() / 1000000.0 << " ms\n";
        std::cout << "  Operations: " << total_operations << "\n";
        std::cout << "  Ops/sec: " << operations_per_second << "\n\n";
    }
};

template<typename RingBufferType>
PerformanceResult measure_single_threaded_performance(size_t buffer_size, size_t num_operations) {
    RingBufferType rb(buffer_size);
    std::atomic<bool> stop_flag{false};
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Fill and empty the buffer multiple times
    for (size_t i = 0; i < num_operations; ++i) {
        while (!rb.produce(static_cast<int>(i), 0, stop_flag)) {
            // Buffer full, consume one item
            int value;
            rb.consume(value, 0, stop_flag);
        }
        
        if (i % 2 == 1) {  // Consume every other item to maintain some items in buffer
            int value;
            rb.consume(value, 0, stop_flag);
        }
    }
    
    // Consume remaining items
    int value;
    while (rb.consume(value, 0, stop_flag)) {}
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    
    size_t ops_per_second = static_cast<size_t>((num_operations * 1000000000.0) / duration.count());
    
    return {duration, ops_per_second, num_operations};
}

template<typename RingBufferType>
PerformanceResult measure_concurrent_performance(size_t buffer_size, size_t num_producers, 
                                               size_t num_consumers, size_t operations_per_thread) {
    RingBufferType rb(buffer_size);
    std::atomic<bool> stop_flag{false};
    std::atomic<size_t> total_operations{0};
    
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    
    // Create producer threads
    for (size_t p = 0; p < num_producers; ++p) {
        producers.emplace_back([&, p]() {
            for (size_t i = 0; i < operations_per_thread; ++i) {
                while (!rb.produce(static_cast<int>(p * operations_per_thread + i), 
                                  static_cast<int>(p), stop_flag) && !stop_flag.load()) {
                    std::this_thread::yield();
                }
                if (stop_flag.load()) break;
                total_operations.fetch_add(1);
            }
        });
    }
    
    // Create consumer threads
    std::atomic<size_t> consumed_count{0};
    for (size_t c = 0; c < num_consumers; ++c) {
        consumers.emplace_back([&, c]() {
            int value;
            size_t expected_total = num_producers * operations_per_thread;
            while (consumed_count.load() < expected_total && !stop_flag.load()) {
                if (rb.consume(value, static_cast<int>(c), stop_flag)) {
                    consumed_count.fetch_add(1);
                } else {
                    std::this_thread::yield();
                }
            }
        });
    }
    
    // Wait for all producers to finish
    for (auto& t : producers) t.join();
    
    // Wait for all consumers to finish
    for (auto& t : consumers) t.join();
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    
    size_t total_ops = total_operations.load();
    size_t ops_per_second = static_cast<size_t>((total_ops * 1000000000.0) / duration.count());
    
    return {duration, ops_per_second, total_ops};
}

class RingBufferPerformanceTest : public ::testing::Test {
protected:
    void SetUp() override {
        std::cout << "\n=== Performance Test Results ===\n\n";
    }
};

TEST_F(RingBufferPerformanceTest, SingleThreadedComparison) {
    const size_t buffer_size = 1024;
    const size_t num_operations = 1000000;
    
    auto mutex_result = measure_single_threaded_performance<MutexRingBuffer>(buffer_size, num_operations);
    auto lockfree_result = measure_single_threaded_performance<LockFreeRingBuffer>(buffer_size, num_operations);
    
    mutex_result.print("MutexRingBuffer (Single-threaded)");
    lockfree_result.print("LockFreeRingBuffer (Single-threaded)");
    
    // Performance comparison
    double speedup = static_cast<double>(lockfree_result.operations_per_second) / 
                    static_cast<double>(mutex_result.operations_per_second);
    
    std::cout << "LockFree vs Mutex speedup: " << speedup << "x\n\n";
    
    // Both should complete successfully
    EXPECT_GT(mutex_result.operations_per_second, 0u);
    EXPECT_GT(lockfree_result.operations_per_second, 0u);
}

TEST_F(RingBufferPerformanceTest, MultiThreadedComparison) {
    const size_t buffer_size = 256;
    const size_t num_producers = 2;
    const size_t num_consumers = 2;
    const size_t operations_per_thread = 100000;
    
    auto mutex_result = measure_concurrent_performance<MutexRingBuffer>(
        buffer_size, num_producers, num_consumers, operations_per_thread);
    auto lockfree_result = measure_concurrent_performance<LockFreeRingBuffer>(
        buffer_size, num_producers, num_consumers, operations_per_thread);
    
    mutex_result.print("MutexRingBuffer (Multi-threaded)");
    lockfree_result.print("LockFreeRingBuffer (Multi-threaded)");
    
    // Performance comparison
    double speedup = static_cast<double>(lockfree_result.operations_per_second) / 
                    static_cast<double>(mutex_result.operations_per_second);
    
    std::cout << "LockFree vs Mutex speedup: " << speedup << "x\n\n";
    
    // Both should complete successfully
    EXPECT_GT(mutex_result.operations_per_second, 0u);
    EXPECT_GT(lockfree_result.operations_per_second, 0u);
    
    // Verify all operations completed
    size_t expected_operations = num_producers * operations_per_thread;
    EXPECT_EQ(mutex_result.total_operations, expected_operations);
    EXPECT_EQ(lockfree_result.total_operations, expected_operations);
}

TEST_F(RingBufferPerformanceTest, HighContentionComparison) {
    const size_t buffer_size = 32;  // Small buffer for high contention
    const size_t num_producers = std::thread::hardware_concurrency() / 2;
    const size_t num_consumers = std::thread::hardware_concurrency() / 2;
    const size_t operations_per_thread = 50000;
    
    if (num_producers == 0 || num_consumers == 0) {
        GTEST_SKIP() << "Insufficient CPU cores for high contention test";
    }
    
    auto mutex_result = measure_concurrent_performance<MutexRingBuffer>(
        buffer_size, num_producers, num_consumers, operations_per_thread);
    auto lockfree_result = measure_concurrent_performance<LockFreeRingBuffer>(
        buffer_size, num_producers, num_consumers, operations_per_thread);
    
    mutex_result.print("MutexRingBuffer (High Contention)");
    lockfree_result.print("LockFreeRingBuffer (High Contention)");
    
    // Performance comparison
    double speedup = static_cast<double>(lockfree_result.operations_per_second) / 
                    static_cast<double>(mutex_result.operations_per_second);
    
    std::cout << "LockFree vs Mutex speedup: " << speedup << "x\n";
    std::cout << "Threads: " << num_producers << " producers, " << num_consumers << " consumers\n\n";
    
    // Both should complete successfully
    EXPECT_GT(mutex_result.operations_per_second, 0u);
    EXPECT_GT(lockfree_result.operations_per_second, 0u);
}

TEST_F(RingBufferPerformanceTest, BufferSizeScalability) {
    const std::vector<size_t> buffer_sizes = {16, 64, 256, 1024, 4096};
    const size_t num_operations = 500000;
    
    std::cout << "Buffer Size Scalability Test:\n";
    std::cout << "Buffer Size | Mutex (ops/sec) | LockFree (ops/sec) | Speedup\n";
    std::cout << "-----------|----------------|-------------------|--------\n";
    
    for (size_t buffer_size : buffer_sizes) {
        auto mutex_result = measure_single_threaded_performance<MutexRingBuffer>(buffer_size, num_operations);
        auto lockfree_result = measure_single_threaded_performance<LockFreeRingBuffer>(buffer_size, num_operations);
        
        double speedup = static_cast<double>(lockfree_result.operations_per_second) / 
                        static_cast<double>(mutex_result.operations_per_second);
        
        std::cout << std::setw(10) << buffer_size << " | "
                  << std::setw(14) << mutex_result.operations_per_second << " | "
                  << std::setw(17) << lockfree_result.operations_per_second << " | "
                  << std::setw(6) << std::fixed << std::setprecision(2) << speedup << "x\n";
        
        // Sanity checks
        EXPECT_GT(mutex_result.operations_per_second, 0u);
        EXPECT_GT(lockfree_result.operations_per_second, 0u);
    }
    std::cout << "\n";
}

// Latency measurement test
TEST_F(RingBufferPerformanceTest, LatencyMeasurement) {
    const size_t buffer_size = 1024;
    const size_t num_samples = 10000;
    
    auto measure_latency = [](auto& rb, size_t samples) {
        std::atomic<bool> stop_flag{false};
        std::vector<std::chrono::nanoseconds> latencies;
        latencies.reserve(samples);
        
        for (size_t i = 0; i < samples; ++i) {
            auto start = std::chrono::high_resolution_clock::now();
            
            // Produce-consume cycle
            rb.produce(static_cast<int>(i), 0, stop_flag);
            int value;
            rb.consume(value, 0, stop_flag);
            
            auto end = std::chrono::high_resolution_clock::now();
            latencies.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(end - start));
        }
        
        std::sort(latencies.begin(), latencies.end());
        
        return std::make_tuple(
            latencies[samples * 0.5],   // median
            latencies[samples * 0.95],  // 95th percentile
            latencies[samples * 0.99]   // 99th percentile
        );
    };
    
    MutexRingBuffer mutex_rb(buffer_size);
    LockFreeRingBuffer lockfree_rb(buffer_size);
    
    auto [mutex_median, mutex_p95, mutex_p99] = measure_latency(mutex_rb, num_samples);
    auto [lockfree_median, lockfree_p95, lockfree_p99] = measure_latency(lockfree_rb, num_samples);
    
    std::cout << "Latency Comparison (nanoseconds):\n";
    std::cout << "Metric      | Mutex    | LockFree | Improvement\n";
    std::cout << "------------|----------|----------|------------\n";
    std::cout << "Median      | " << std::setw(8) << mutex_median.count() 
              << " | " << std::setw(8) << lockfree_median.count()
              << " | " << std::setw(6) << std::fixed << std::setprecision(2) 
              << (static_cast<double>(mutex_median.count()) / lockfree_median.count()) << "x\n";
    std::cout << "95th perc.  | " << std::setw(8) << mutex_p95.count() 
              << " | " << std::setw(8) << lockfree_p95.count()
              << " | " << std::setw(6) << std::fixed << std::setprecision(2) 
              << (static_cast<double>(mutex_p95.count()) / lockfree_p95.count()) << "x\n";
    std::cout << "99th perc.  | " << std::setw(8) << mutex_p99.count() 
              << " | " << std::setw(8) << lockfree_p99.count()
              << " | " << std::setw(6) << std::fixed << std::setprecision(2) 
              << (static_cast<double>(mutex_p99.count()) / lockfree_p99.count()) << "x\n\n";
    
    // Verify that measurements are reasonable
    EXPECT_GT(mutex_median.count(), 0);
    EXPECT_GT(lockfree_median.count(), 0);
    EXPECT_GE(mutex_p95.count(), mutex_median.count());
    EXPECT_GE(lockfree_p95.count(), lockfree_median.count());
}