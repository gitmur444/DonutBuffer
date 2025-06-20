export module simulation_manager;

#include <memory>
#include <vector>
#include <atomic>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstddef>
#include <functional>

// Forward declare ring buffer adapter and performance history
class AbstractRingBuffer;
class PerformanceHistory;

export class SimulationManager {
public:
    SimulationManager();
    ~SimulationManager();

    void start(int producers, int consumers, int buffer_size);
    void stop();
    bool is_running() const;
    // ... другие публичные методы ...

private:
    // ... приватные данные и методы ...
};
