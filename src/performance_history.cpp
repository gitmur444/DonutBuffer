#include "performance_history.h"
#include <algorithm>

// Global instance for easy access
PerformanceHistory g_performance_history;

PerformanceHistory::PerformanceHistory(size_t max_points, unsigned int min_update_interval_ms) 
    : max_history_points(max_points),
      max_speed(0.0f),
      min_update_interval(min_update_interval_ms),
      last_update_time(std::chrono::steady_clock::now()) {
    // Reserve space to avoid frequent reallocations
    throughput_history.reserve(max_points);
    run_markers.reserve(50); // Reducing from 100 to 50 - still plenty for most use cases
}

void PerformanceHistory::add_data_point(double throughput_speed) {
    std::lock_guard<std::mutex> lock(history_mutex);
    
    // Check if enough time has passed since the last update
    auto current_time = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - last_update_time);
    
    if (elapsed < min_update_interval) {
        // Not enough time has passed, skip this update
        return;
    }
    
    // Update the last update time
    last_update_time = current_time;
    
    // Add new data point
    throughput_history.push_back(static_cast<float>(throughput_speed));
    
    // Update max speed
    max_speed = std::max(max_speed, static_cast<float>(throughput_speed));
    
    // Trim if exceeded max size
    if (throughput_history.size() > max_history_points) {
        // Remove oldest points
        throughput_history.erase(throughput_history.begin());
        
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
    if (!throughput_history.empty()) {
        run_markers.push_back(static_cast<int>(throughput_history.size()) - 1);
    }
}

const std::vector<float>& PerformanceHistory::get_throughput_history() const {
    return throughput_history;
}

const std::vector<int>& PerformanceHistory::get_run_markers() const {
    return run_markers;
}

void PerformanceHistory::clear() {
    std::lock_guard<std::mutex> lock(history_mutex);
    throughput_history.clear();
    run_markers.clear();
    max_speed = 0.0f;
}



float PerformanceHistory::get_max_speed() const {
    return max_speed;
}
