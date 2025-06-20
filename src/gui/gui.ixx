export module gui;

#include <string>
#include <vector>
#include <thread>        // For std::thread, if used directly in exported symbols (likely not for .ixx)
#include <atomic>        // For std::atomic, if used directly in exported symbols
#include <mutex>         // For std::mutex, e.g., log_mutex
#include <list>          // For std::list, e.g., event_log
#include <memory>        // For std::unique_ptr, if used in exported symbols
#include <functional>    // For std::function

// Forward declarations
struct GLFWwindow;
// class RingBuffer; // Forward declare if RingBuffer type appears in any exported function signatures or variables

// --- Configuration Constants ---
export extern const int MAX_BUFFER_SIZE;
export extern const int MAX_PRODUCERS;
export extern const int MAX_CONSUMERS;
export extern const size_t MAX_LOG_ENTRIES;

// --- Global State for GUI ---
export extern int num_producers_gui;
export extern int num_consumers_gui;
export extern int buffer_size_gui;

// Speed measurement variables
export extern double producer_speed_gui;
export extern double consumer_speed_gui;
export extern size_t total_produced_gui;
export extern size_t total_consumed_gui;

// Performance graph controls
export extern bool show_producer_graph;
export extern bool show_consumer_graph;

export extern std::mutex log_mutex; // For add_log
export extern std::list<std::string> event_log;

// --- Platform and Window Initialization ---
export bool initialize_platform_and_window(GLFWwindow*& out_window, const char*& out_glsl_version, int width, int height, const char* title);

// --- GUI and Simulation Control Functions ---
export void init_gui_components(GLFWwindow* window, const char* glsl_version);
export void render_gui_frame();
export void shutdown_gui_components();

export void add_log(const std::string& message);

// --- GLFW Error Callback ---
export void glfw_error_callback(int error, const char* description);

// --- GUI Event Callbacks & State Update Functions ---
export namespace gui_events {
    export extern std::function<void(int)> on_buffer_impl_changed;
    export extern std::function<void(int /*producers*/, int /*consumers*/, int /*buffer_size*/)> on_start_simulation_request;
    export extern std::function<void()> on_stop_simulation_request;
    
    export extern std::function<void(int /*new_count*/)> on_producer_count_update;
    export extern std::function<void(int /*new_count*/)> on_consumer_count_update;
    export extern std::function<void(int /*new_size*/)> on_buffer_size_update;
}

// Functions for external logic (Application) to update GUI state
export void set_gui_simulation_active_status(bool is_active);
export void set_gui_buffer_stats(size_t item_count, size_t capacity);
export void set_gui_speed_stats(double producer_speed, double consumer_speed, size_t total_produced, size_t total_consumed);
export void gui_main_loop(std::function<void()> on_update);
