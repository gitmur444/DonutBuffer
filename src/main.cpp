#include "flags.h"         // Command line flag parsing
#include "experiments/mutex_vs_lockfree_experiment.h"
#include "experiments/concurrent_vs_lockfree_experiment.h"

#include "ringbuffer/lockfree_ring_buffer_adapter.h"
#include "ringbuffer/mutex_ring_buffer_adapter.h"
#include "ringbuffer/abstract_ring_buffer.h"

#include <iostream>
#include <memory>
#include <atomic>
#include <thread>
#include <vector>
#include <chrono>

namespace {

std::unique_ptr<AbstractRingBuffer> create_buffer(const std::string& type,
                                                 size_t capacity) {
    if (type == "lockfree") {
        return std::make_unique<LockFreeRingBufferAdapter>(capacity);
    }
    return std::make_unique<MutexRingBufferAdapter>(capacity);
}

void run_benchmark(AbstractRingBuffer* buffer, int producers, int consumers,
                   int num_items) {
    std::atomic<bool> stop_flag{false};
    std::atomic<int> produced{0};
    std::atomic<int> consumed{0};
    std::vector<std::thread> prod_threads, cons_threads;

    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < producers; ++i) {
        prod_threads.emplace_back([&, i]() {
            while (!stop_flag.load()) {
                int item = produced.fetch_add(1);
                if (item >= num_items) break;
                while (!buffer->produce(item, i, stop_flag)) {
                    if (stop_flag.load()) return;
                }
            }
        });
    }

    for (int i = 0; i < consumers; ++i) {
        cons_threads.emplace_back([&, i]() {
            int item;
            while (!stop_flag.load()) {
                if (consumed.load() >= num_items) break;
                if (buffer->consume(item, i, stop_flag)) {
                    consumed.fetch_add(1);
                }
            }
        });
    }

    while (consumed.load() < num_items) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    stop_flag = true;
    buffer->notify_all_on_stop();

    for (auto& t : prod_threads) t.join();
    for (auto& t : cons_threads) t.join();

    auto end = std::chrono::high_resolution_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();
    std::cout << "Finished in " << seconds << " sec, "
              << (num_items / seconds) << " items/sec" << std::endl;
}

} // namespace

int main(int argc, char** argv) {
    AppFlags flags = parse_flags(argc, argv);

    if (flags.mutex_vs_lockfree) {
        MutexVsLockfreeExperiment().run();
        return 0;
    }

    if (flags.concurrent_vs_lockfree) {
        ConcurrentVsLockfreeExperiment().run();
        return 0;
    }

    const size_t buffer_capacity =
        static_cast<size_t>(flags.buffer_config.buffer_size_mb) * 1024 * 1024 / sizeof(int);
    const int num_items = static_cast<int>(
        flags.buffer_config.total_transfer_mb * 1024 * 1024ULL / sizeof(int));

    auto buffer = create_buffer(flags.buffer_config.buffer_type, buffer_capacity);
    if (!buffer) {
        std::cerr << "Unknown buffer type: " << flags.buffer_config.buffer_type << std::endl;
        return 1;
    }

    std::cout << "Running " << flags.buffer_config.buffer_type
              << " with P=" << flags.buffer_config.producer_count
              << " C=" << flags.buffer_config.consumer_count << std::endl;

    run_benchmark(buffer.get(), flags.buffer_config.producer_count,
                  flags.buffer_config.consumer_count, num_items);
    return 0;
}
