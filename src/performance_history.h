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
    PerformanceHistory(size_t max_points = 1000);
    
    // Add new data point
    void add_data_point(double producer_speed, double consumer_speed);
    
    // Mark a new run starting
    void mark_new_run();
    
    // Get history data
    const std::vector<float>& get_producer_history() const;
    const std::vector<float>& get_consumer_history() const;
    const std::vector<int>& get_run_markers() const;
    
    // Clear history
    void clear();
    
    // Get statistics
    float get_max_producer_speed() const;
    float get_max_consumer_speed() const;
    float get_max_speed() const; // Maximum of both speeds

private:
    std::vector<float> producer_history;
    std::vector<float> consumer_history;
    std::vector<int> run_markers; // Indices where new runs start
    size_t max_history_points;
    
    float max_producer_speed;
    float max_consumer_speed;
    
    std::mutex history_mutex;
};

// Global instance for easy access
extern PerformanceHistory g_performance_history;

#endif // PERFORMANCE_HISTORY_H
