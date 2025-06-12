#ifndef GUI_H
#define GUI_H

#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <list>
#include <memory> // For std::unique_ptr
#include <functional> // For std::function

// Forward declarations
struct GLFWwindow;
class RingBuffer;

// --- Configuration Constants ---
extern const int MAX_BUFFER_SIZE;
extern const int MAX_PRODUCERS;
extern const int MAX_CONSUMERS;
extern const size_t MAX_LOG_ENTRIES;

// --- Global State for GUI (declared extern, defined in gui.cpp) ---

extern int num_producers_gui;
extern int num_consumers_gui;
extern int buffer_size_gui;

// Speed measurement variables
extern double producer_speed_gui;
extern double consumer_speed_gui;
extern size_t total_produced_gui;
extern size_t total_consumed_gui;

// Performance graph controls
extern bool show_producer_graph;
extern bool show_consumer_graph;

extern std::mutex log_mutex; // For add_log
extern std::list<std::string> event_log;

// --- Platform and Window Initialization ---
// Initializes GLFW, creates a window, and initializes GLAD.
// Returns true on success, false on failure.
// Outputs the created GLFWwindow* and the determined GLSL version string.
bool initialize_platform_and_window(GLFWwindow*& out_window, const char*& out_glsl_version, int width, int height, const char* title);

// --- GUI and Simulation Control Functions ---
void init_gui_components(GLFWwindow* window, const char* glsl_version);
void render_gui_frame();
void shutdown_gui_components();

void add_log(const std::string& message);

// --- GLFW Error Callback ---
void glfw_error_callback(int error, const char* description);

// --- GUI Event Callbacks & State Update Functions ---
namespace gui_events {
    // Callbacks for GUI to signal actions to the application logic
    extern std::function<void(int /*producers*/, int /*consumers*/, int /*buffer_size*/)> on_start_simulation_request;
    extern std::function<void()> on_stop_simulation_request;
}

// Functions for external logic (Application) to update GUI state
void set_gui_simulation_active_status(bool is_active);
void set_gui_buffer_stats(size_t item_count, size_t capacity);
void set_gui_speed_stats(double producer_speed, double consumer_speed, size_t total_produced, size_t total_consumed);


#endif // GUI_H
