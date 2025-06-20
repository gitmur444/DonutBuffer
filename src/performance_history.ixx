export module performance_history;

#include <vector>
#include <chrono> // For std::chrono types
#include <mutex>   // For std::mutex

export class PerformanceHistory {
public:
    PerformanceHistory(size_t max_points = 1000);
    void add_sample(float value);
    void mark_new_run();
    const std::vector<float>& get_throughput_history() const;
    const std::vector<int>& get_run_markers() const;
    void clear();
    float get_max_speed() const;
private:
    std::vector<float> throughput_history;
    std::vector<int> run_markers;
    size_t max_history_points;
    float max_speed;
    std::chrono::milliseconds min_update_interval;
    std::chrono::steady_clock::time_point last_update_time;
    std::mutex history_mutex;
};

export extern PerformanceHistory g_performance_history;
