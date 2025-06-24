#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <memory>

#include "ringbuffer/lockfree_ring_buffer_adapter.h"
#include "ringbuffer/mutex_ring_buffer_adapter.h"
#include "ringbuffer/abstract_ring_buffer.h"

namespace {
std::unique_ptr<AbstractRingBuffer> create_buffer(const std::string& type, size_t capacity) {
    if (type == "lockfree") {
        return std::make_unique<LockFreeRingBufferAdapter>(capacity);
    }
    return std::make_unique<MutexRingBufferAdapter>(capacity);
}

void run_benchmark(AbstractRingBuffer* buffer, int producers, int consumers, int num_items) {
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
    std::string type = "mutex";
    int producers = 1;
    int consumers = 1;
    const int num_items = 100000; // default number of items
    const size_t buffer_size = 8;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg.rfind("--type=", 0) == 0) {
            type = arg.substr(7);
        } else if (arg.rfind("--producers=", 0) == 0) {
            producers = std::stoi(arg.substr(12));
        } else if (arg.rfind("--consumers=", 0) == 0) {
            consumers = std::stoi(arg.substr(12));
        }
    }

    auto buffer = create_buffer(type, buffer_size);
    if (!buffer) {
        std::cerr << "Unknown buffer type: " << type << std::endl;
        return 1;
    }

    std::cout << "Running " << type << " with P=" << producers
              << " C=" << consumers << std::endl;
    run_benchmark(buffer.get(), producers, consumers, num_items);
    return 0;
}
