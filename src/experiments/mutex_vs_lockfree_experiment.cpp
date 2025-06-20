#include "ringbuffer/mutex_ring_buffer_adapter.h"
#include "ringbuffer/lockfree_ring_buffer_adapter.h"
#include "mutex_vs_lockfree_experiment.h"
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>

constexpr int NUM_ITEMS = 1000000;
constexpr int BUFFER_SIZE = 8;
constexpr int NUM_PRODUCERS = 4;
constexpr int NUM_CONSUMERS = 4;

static void run_benchmark(AbstractRingBuffer* buffer, const std::string& name) {
    std::atomic<bool> stop_flag{false};
    std::atomic<int> produced{0};
    std::atomic<int> consumed{0};
    std::vector<std::thread> producers, consumers;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < NUM_PRODUCERS; ++i) {
        producers.emplace_back([&, i]() {
            while (!stop_flag) {
                int item = produced.fetch_add(1);
                if (item >= NUM_ITEMS) break;
                while (!buffer->produce(item, i, stop_flag)) {
                    if (stop_flag) return;
                }
            }
        });
    }
    for (int i = 0; i < NUM_CONSUMERS; ++i) {
        consumers.emplace_back([&, i]() {
            int item;
            while (!stop_flag) {
                if (consumed.load() >= NUM_ITEMS) break;
                if (buffer->consume(item, i, stop_flag)) {
                    consumed.fetch_add(1);
                }
            }
        });
    }
    while (consumed.load() < NUM_ITEMS) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    stop_flag = true;
    buffer->notify_all_on_stop();
    for (auto& t : producers) t.join();
    for (auto& t : consumers) t.join();
    auto end = std::chrono::high_resolution_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();
    std::cout << name << ": " << NUM_ITEMS << " items, " << seconds << " sec, " << (NUM_ITEMS / seconds) << " items/sec" << std::endl;
}

MutexVsLockfreeExperiment::MutexVsLockfreeExperiment() { ExperimentBase::register_experiment(this); }
MutexVsLockfreeExperiment MutexVsLockfreeExperiment::instance;

void MutexVsLockfreeExperiment::run() {
    std::cout << "Mutex vs Lock-Free Ring Buffer Benchmark" << std::endl;
    AbstractRingBuffer* mutex_rb = new MutexRingBufferAdapter(BUFFER_SIZE);
    run_benchmark(mutex_rb, "MutexRingBuffer");
    delete mutex_rb;
    AbstractRingBuffer* lockfree_rb = new LockFreeRingBufferAdapter(BUFFER_SIZE);
    run_benchmark(lockfree_rb, "LockFreeRingBuffer");
    delete lockfree_rb;
}
