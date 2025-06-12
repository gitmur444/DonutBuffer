#include "performance_history.h"
#include <algorithm>

// Global instance for easy access
PerformanceHistory g_performance_history;

PerformanceHistory::PerformanceHistory(size_t max_points) 
    : max_history_points(max_points),
      max_producer_speed(0.0f),
      max_consumer_speed(0.0f) {
    // Reserve space to avoid frequent reallocations
    producer_history.reserve(max_points);
    consumer_history.reserve(max_points);
    run_markers.reserve(100); // Assuming fewer than 100 runs
}

void PerformanceHistory::add_data_point(double producer_speed, double consumer_speed) {
    std::lock_guard<std::mutex> lock(history_mutex);
    
    // Add new data points
    producer_history.push_back(static_cast<float>(producer_speed));
    consumer_history.push_back(static_cast<float>(consumer_speed));
    
    // Update max speeds
    max_producer_speed = std::max(max_producer_speed, static_cast<float>(producer_speed));
    max_consumer_speed = std::max(max_consumer_speed, static_cast<float>(consumer_speed));
    
    // Trim if exceeded max size
    if (producer_history.size() > max_history_points) {
        // Remove oldest points
        producer_history.erase(producer_history.begin());
        consumer_history.erase(consumer_history.begin());
        
        // Adjust run markers
        for (auto& marker : run_markers) {
            marker--;
        }
        
        // Remove any negative markers
        run_markers.erase(
            std::remove_if(run_markers.begin(), run_markers.end(), 
                          [](int x) { return x < 0; }),
            run_markers.end()
        );
    }
}

void PerformanceHistory::mark_new_run() {
    std::lock_guard<std::mutex> lock(history_mutex);
    
    // Add marker at current position in history
    if (!producer_history.empty()) {
        run_markers.push_back(static_cast<int>(producer_history.size()) - 1);
    }
}

const std::vector<float>& PerformanceHistory::get_producer_history() const {
    return producer_history;
}

const std::vector<float>& PerformanceHistory::get_consumer_history() const {
    return consumer_history;
}

const std::vector<int>& PerformanceHistory::get_run_markers() const {
    return run_markers;
}

void PerformanceHistory::clear() {
    std::lock_guard<std::mutex> lock(history_mutex);
    producer_history.clear();
    consumer_history.clear();
    run_markers.clear();
    max_producer_speed = 0.0f;
    max_consumer_speed = 0.0f;
}

float PerformanceHistory::get_max_producer_speed() const {
    return max_producer_speed;
}

float PerformanceHistory::get_max_consumer_speed() const {
    return max_consumer_speed;
}

float PerformanceHistory::get_max_speed() const {
    return std::max(max_producer_speed, max_consumer_speed);
}
