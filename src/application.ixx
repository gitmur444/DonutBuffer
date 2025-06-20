export module application;

// Forward declare GLFWwindow to avoid including glfw3.h in the header if possible
struct GLFWwindow;

export class Application {
public:
    Application();
    ~Application();

    bool initialize(int width, int height, const char* title);
    void run_main_loop();
    void shutdown();

private:
    GLFWwindow* window = nullptr;
    bool initialized = false;
    bool shutdown_called = false;
    std::unique_ptr<class SimulationManager> simulationManager;

    void handle_start_simulation_request(int producers, int consumers, int buffer_size);
    void handle_stop_simulation_request();
    void handle_producer_count_update(int new_count);
    void handle_consumer_count_update(int new_count);
    void handle_buffer_size_update(int new_size);
};
