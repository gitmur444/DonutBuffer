#include "application.h" // Assuming Application class is defined here
#include "gui/gui.h"       // Assuming GUI related functions/classes are here
#include "flags.h"         // Assuming AppFlags and parse_flags are defined here
#include "experiments/experiment_base.h" // Assuming ExperimentBase is here

#include "ringbuffer/lockfree_ring_buffer_adapter.h"
#include "ringbuffer/mutex_ring_buffer_adapter.h"
#include "ringbuffer/abstract_ring_buffer.h"

#include "imgui.h" // For ImVec4, ImGui::GetDrawData. This is a C library, so it remains an include.
#include <iostream> // For std::cerr in case of critical app init failure
#include <filesystem>
#include <cstdlib>
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
    // Run experiment if requested, then exit
    /*
    if (ExperimentBase::try_run_experiment(flags.args)) {
        return 0;
    }

    if (flags.nogui) {
        std::cout << "Running in --nogui mode (no GUI, no simulation logic implemented yet)" << std::endl;
        // Здесь можно добавить headless-режим или тесты без GUI
        return 0;
    }
    Application app;
    if (!app.initialize(1280, 720, "Ring Buffer GUI - Refactored")) {
        std::cerr << "FATAL: Application initialization failed. Check log for details." << std::endl;
        return -1;
    }
    app.run_main_loop();
    app.shutdown();
    */

    const int num_items = 100000;
    const size_t buffer_size = 8;

    auto buffer = create_buffer(flags.type, buffer_size);
    if (!buffer) {
        std::cerr << "Unknown buffer type: " << flags.type << std::endl;
        return 1;
    }

    std::cout << "Running " << flags.type << " with P=" << flags.producers
              << " C=" << flags.consumers << std::endl;

    run_benchmark(buffer.get(), flags.producers, flags.consumers, num_items);

    return 0;
}
