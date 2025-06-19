#ifndef PERFORMANCE_HISTORY_H
#define PERFORMANCE_HISTORY_H

#include <vector>
#include <deque>
#include <string>
#include <mutex>
#include <chrono>

// Class to store performance metrics history across simulation runs
class PerformanceHistory {
public:
    // Reduced max_points default to 500, and added min_update_interval_ms with default of 500 ms
    PerformanceHistory(size_t max_points = 500, unsigned int min_update_interval_ms = 500);
    
    // Add new data point - simplified to use single throughput metric
    void add_data_point(double throughput_speed);
    
    // Mark a new run starting
    void mark_new_run();
    
    // Get history data
    const std::vector<float>& get_throughput_history() const;
    const std::vector<int>& get_run_markers() const;
    
    // Clear history
    void clear();
    
    // Get statistics
    float get_max_speed() const;

private:
    std::vector<float> throughput_history;
    std::vector<int> run_markers; // Indices where new runs start
    size_t max_history_points;
    
    float max_speed;
    
    // Rate limiting for data points
    std::chrono::milliseconds min_update_interval;
    std::chrono::steady_clock::time_point last_update_time;
    
    std::mutex history_mutex;
};

// Global instance for easy access
extern PerformanceHistory g_performance_history;

#endif // PERFORMANCE_HISTORY_H
