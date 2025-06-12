#ifndef APPLICATION_H
#define APPLICATION_H

// Forward declare GLFWwindow to avoid including glfw3.h in the header if possible,
// though gui.h (which Application will use) already includes it via simulation_manager.h -> ring_buffer.h -> etc.
// For simplicity here, we might just #include <string>
#include <memory>
#include <functional> // For std::function if needed, though callbacks are global
#include "simulation_manager.h" // Include SimulationManager header rely on transitive includes.
struct GLFWwindow; // From GLFW

class Application {
public:
    Application();
    ~Application();

    // Initializes the application, including platform, window, and GUI components.
    // Returns true on success, false on failure.
    bool initialize(int width, int height, const char* title);

    // Runs the main application loop.
    void run_main_loop();

    // Shuts down the application, cleaning up resources.
    void shutdown();

private:
    GLFWwindow* window = nullptr;
    // const char* glsl_version_ = nullptr; // glsl_version is managed by gui/platform init and ImGui backends
    bool initialized = false;
    bool shutdown_called = false; // To prevent double shutdown in destructor
    std::unique_ptr<SimulationManager> simulationManager;

    // Private helpers to handle GUI requests
    void handle_start_simulation_request(int producers, int consumers, int buffer_size);
    void handle_stop_simulation_request();
    
    // Обработчики для динамического изменения параметров
    void handle_producer_count_update(int new_count);
    void handle_consumer_count_update(int new_count);
    void handle_buffer_size_update(int new_size);
};

#endif // APPLICATION_H
