#include "simulation_manager.h"
#include <iostream> // For potential std::cerr, though logger is preferred
#include <chrono>   // For std::chrono::milliseconds
#include <sstream>  // For std::ostringstream

// Helper to format log messages with thread ID
std::string format_thread_log(const std::string& message, int id, const std::string& type) {
    std::ostringstream oss;
    oss << "[" << type << " " << id << " TID:" << std::this_thread::get_id() << "] " << message;
    return oss.str();
}

SimulationManager::SimulationManager(std::function<void(const std::string&)> logger)
    : simulation_active(false),
      stop_flag(false),
      num_producers_cfg(1),
      num_consumers_cfg(1),
      buffer_size_cfg(10),
      logger_func(logger) {
    log("SimulationManager created.");
}

SimulationManager::~SimulationManager() {
    log("SimulationManager destroying...");
    if (simulation_active.load() || !producer_threads.empty() || !consumer_threads.empty()) {
        request_stop();
        join_threads();
    }
    log("SimulationManager destroyed.");
}

void SimulationManager::log(const std::string& message) {
    if (logger_func) {
        logger_func(message);
    }
}

void SimulationManager::configure(int producers, int consumers, int buffer_size) {
    if (simulation_active.load()) {
        log("Cannot configure while simulation is active. Please stop it first.");
        return;
    }
    num_producers_cfg = producers;
    num_consumers_cfg = consumers;
    buffer_size_cfg = buffer_size;
    log("Simulation configured: P=" + std::to_string(producers) + 
        ", C=" + std::to_string(consumers) + ", BS=" + std::to_string(buffer_size));
}

void SimulationManager::start() {
    if (simulation_active.load()) {
        log("Simulation already running.");
        return;
    }

    log("Starting simulation...");
    
    // Reset the buffer if it exists
    if (ring_buffer_ptr) {
        reset_buffer();
    }
    
    // Create new buffer
    ring_buffer_ptr = std::make_unique<RingBuffer>(static_cast<size_t>(buffer_size_cfg));
    
    // Reset stop flag and speed counters
    stop_flag.store(false);
    total_produced.store(0);
    total_consumed.store(0);
    producer_speed.store(0.0);
    consumer_speed.store(0.0);
    
    // Start timing
    start_time = std::chrono::steady_clock::now();
    speed_measurement_active.store(true);
    
    // Start producer and consumer threads
    for (int i = 0; i < num_producers_cfg; ++i) {
        producer_threads.emplace_back(&SimulationManager::producer_task_impl, this, i + 1);
    }
    
    for (int i = 0; i < num_consumers_cfg; ++i) {
        consumer_threads.emplace_back(&SimulationManager::consumer_task_impl, this, i + 1);
    }
    
    simulation_active.store(true);
    log("Simulation started.");
}

void SimulationManager::request_stop() {
    if (!simulation_active.load()) {
        log("No simulation running.");
        return;
    }

    log("Requesting simulation to stop...");
    stop_flag.store(true);
    speed_measurement_active.store(false);
    if (ring_buffer_ptr) {
        ring_buffer_ptr->notify_all_on_stop(); 
    }
}

void SimulationManager::join_threads() {
    log("Joining producer threads...");
    for (auto& t : producer_threads) {
        if (t.joinable()) {
            t.join();
        }
    }
    producer_threads.clear();
    log("Producer threads joined.");

    log("Joining consumer threads...");
    for (auto& t : consumer_threads) {
        if (t.joinable()) {
            t.join();
        }
    }
    consumer_threads.clear();
    log("Consumer threads joined.");
    
    simulation_active.store(false); // Mark as inactive after threads are joined
    log("All simulation threads joined.");
}

void SimulationManager::reset_buffer() {
    if (simulation_active.load()) {
        log("Cannot reset buffer while simulation is active.");
        return;
    }
    ring_buffer_ptr.reset(); // Destroys the old RingBuffer
    log("RingBuffer reset.");
}

bool SimulationManager::is_active() const {
    return simulation_active.load();
}

size_t SimulationManager::get_buffer_item_count() const {
    if (ring_buffer_ptr) {
        return ring_buffer_ptr->get_count();
    }
    return 0;
}

size_t SimulationManager::get_buffer_capacity() const {
    if (ring_buffer_ptr) {
        return ring_buffer_ptr->get_capacity();
    }
    // Return configured capacity if buffer not yet created, or 0
    return static_cast<size_t>(buffer_size_cfg); 
}

double SimulationManager::get_producer_speed() const {
    return producer_speed.load();
}

double SimulationManager::get_consumer_speed() const {
    return consumer_speed.load();
}

size_t SimulationManager::get_total_produced() const {
    return total_produced.load();
}

size_t SimulationManager::get_total_consumed() const {
    return total_consumed.load();
}

// --- Thread Implementations ---
void SimulationManager::producer_task_impl(int id) {
    log(format_thread_log("started.", id, "Producer"));
    int item_produced_count = 0;
    while (!stop_flag.load()) {
        int item = rand() % 1000; // Produce a random item
        if (ring_buffer_ptr && ring_buffer_ptr->produce(item, id, stop_flag)) {
            item_produced_count++;
            total_produced.fetch_add(1);
            
            // Update speed measurements periodically
            if (speed_measurement_active.load() && item_produced_count % 10 == 0) {
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
                if (elapsed > 0) {
                    double speed = static_cast<double>(total_produced.load()) * 1000.0 / elapsed;
                    producer_speed.store(speed);
                }
            }
            
            // Log periodically or on specific events to avoid flooding
            if (item_produced_count % 10 == 0) { 
                 log(format_thread_log("produced item #" + std::to_string(item_produced_count) + ": " + std::to_string(item), id, "Producer"));
            }
        } else {
            if (stop_flag.load()) {
                log(format_thread_log("stop signal received, exiting.", id, "Producer"));
                break;
            }
            // Buffer might be full or other condition, short pause
            std::this_thread::sleep_for(std::chrono::milliseconds(10)); 
        }
    }
    log(format_thread_log("finished. Total items produced: " + std::to_string(item_produced_count), id, "Producer"));
}

void SimulationManager::consumer_task_impl(int id) {
    log(format_thread_log("started.", id, "Consumer"));
    int item_consumed_count = 0;
    int item;
    while (!stop_flag.load()) {
        if (ring_buffer_ptr && ring_buffer_ptr->consume(item, id, stop_flag)) {
            item_consumed_count++;
            total_consumed.fetch_add(1);
            
            // Update speed measurements periodically
            if (speed_measurement_active.load() && item_consumed_count % 10 == 0) {
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
                if (elapsed > 0) {
                    double speed = static_cast<double>(total_consumed.load()) * 1000.0 / elapsed;
                    consumer_speed.store(speed);
                }
            }
            
            if (item_consumed_count % 10 == 0) { 
                log(format_thread_log("consumed item #" + std::to_string(item_consumed_count) + ": " + std::to_string(item), id, "Consumer"));
            }
        } else {
            if (stop_flag.load()) {
                log(format_thread_log("stop signal received, exiting.", id, "Consumer"));
                break;
            }
            // Buffer might be empty or other condition, short pause
            std::this_thread::sleep_for(std::chrono::milliseconds(10)); 
        }
    }
    log(format_thread_log("finished. Total items consumed: " + std::to_string(item_consumed_count), id, "Consumer"));
}

