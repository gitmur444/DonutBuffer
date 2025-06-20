#ifndef SIMULATION_MANAGER_H
#define SIMULATION_MANAGER_H

#include "ringbuffer/abstract_ring_buffer.h"
#include "ringbuffer/mutex_ring_buffer_adapter.h"
#include <vector>
#include <thread>
#include <atomic>
#include <memory>
#include <functional>
#include <string>
#include <chrono>

enum class RingBufferType { Custom, ConcurrentQueue };

class SimulationManager {
public:
    void set_buffer_type(RingBufferType type);
    RingBufferType get_buffer_type() const;

    SimulationManager(std::function<void(const std::string&)> logger);
    ~SimulationManager();

    void configure(int producers, int consumers, int buffer_size);
    void start();
    void request_stop();
    void join_threads(); // Waits for threads to complete
    void reset_buffer();   // Clears the ring buffer
    
    // Dynamic configuration methods
    void update_producers(int new_producer_count);
    void update_consumers(int new_consumer_count);
    void update_buffer_size(int new_buffer_size);

    bool is_active() const;
    size_t get_buffer_item_count() const;
    size_t get_buffer_capacity() const;
    
    // Speed measurement methods
    double get_producer_speed() const; // items per second
    double get_consumer_speed() const; // items per second
    size_t get_total_produced() const;
    size_t get_total_consumed() const;

private:
    void producer_task_impl(int id);
    void consumer_task_impl(int id);
    void log(const std::string& message);

    std::unique_ptr<AbstractRingBuffer> ring_buffer_ptr;
    std::vector<std::thread> producer_threads;
    std::vector<std::thread> consumer_threads;
    
    std::atomic<bool> simulation_active;
    std::atomic<bool> stop_flag;

    int num_producers_cfg;
    int num_consumers_cfg;
    int buffer_size_cfg;

    std::function<void(const std::string&)> logger_func;
    
    // Speed measurement variables
    std::atomic<size_t> total_produced{0};
    std::atomic<size_t> total_consumed{0};
    std::chrono::steady_clock::time_point start_time;
    RingBufferType buffer_type = RingBufferType::Custom;
    std::atomic<double> producer_speed{0.0};
    std::atomic<double> consumer_speed{0.0};
    std::atomic<bool> speed_measurement_active{false};
};

#endif // SIMULATION_MANAGER_H
