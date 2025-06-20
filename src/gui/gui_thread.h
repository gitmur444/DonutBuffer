#ifndef GUI_THREAD_H
#define GUI_THREAD_H

#include <thread>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <memory>
#include <vector>
#include <string>

// Forward declarations
struct GLFWwindow;
class SimulationManager;

/**
 * Class to run GUI rendering in a separate thread
 */
class GUIThread {
public:
    GUIThread();
    ~GUIThread();
    
    // Initialize and start the GUI thread
    bool init(SimulationManager* simManager, GLFWwindow* window);
    
    // Stop GUI thread
    void stop();
    
    // Check if window should close
    bool should_close() const;
    
    // Add log entry (thread-safe)
    void add_log(const std::string& log);
    
    // Wait for GUI to initialize
    void wait_for_initialization();
    
    // Notify about simulation state changes
    void notify_simulation_changed();
    
private:
    // GUI thread main function
    void gui_thread_func();
    
    // Member variables
    std::thread gui_thread;
    std::atomic<bool> stop_flag;
    std::atomic<bool> initialized;
    std::atomic<bool> window_should_close;
    
    // Synchronization primitives
    std::mutex gui_mutex;
    std::condition_variable init_cv;
    std::condition_variable update_cv;
    std::atomic<bool> simulation_changed;
    
    // Access to application state
    SimulationManager* simulation_manager;
    GLFWwindow* window;
    
    // Thread local log buffer (to avoid mutex contention for every log entry)
    std::vector<std::string> pending_logs;
};

// Global GUI thread instance (similar to g_performance_history)
extern GUIThread g_gui_thread;

#endif // GUI_THREAD_H
