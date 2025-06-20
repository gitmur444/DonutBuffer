#include "gui/gui_thread.h"
#include "simulation_manager.h"
#include "performance_history.h"
#include "gui/gui.h"

#include <GLFW/glfw3.h>
#include <chrono>
#include <thread>
#include <iostream>

// Global instance
GUIThread g_gui_thread;

GUIThread::GUIThread() 
    : stop_flag(false), 
      initialized(false),
      window_should_close(false),
      simulation_changed(false),
      simulation_manager(nullptr),
      window(nullptr) {
}

GUIThread::~GUIThread() {
    stop();
}

bool GUIThread::init(SimulationManager* simManager, GLFWwindow* win) {
    if (gui_thread.joinable()) {
        return false; // Already running
    }
    
    simulation_manager = simManager;
    window = win;
    stop_flag = false;
    initialized = false;
    window_should_close = false;
    
    // Start thread
    gui_thread = std::thread(&GUIThread::gui_thread_func, this);
    
    // Wait for initialization
    wait_for_initialization();
    
    return true;
}

void GUIThread::stop() {
    if (gui_thread.joinable()) {
        stop_flag = true;
        notify_simulation_changed(); // Wake up thread if waiting
        gui_thread.join();
    }
}

bool GUIThread::should_close() const {
    return window_should_close.load();
}

void GUIThread::add_log(const std::string& log) {
    std::lock_guard<std::mutex> lock(gui_mutex);
    pending_logs.push_back(log);
}

void GUIThread::wait_for_initialization() {
    if (!initialized.load()) {
        std::unique_lock<std::mutex> lock(gui_mutex);
        init_cv.wait(lock, [this]() { return initialized.load(); });
    }
}

void GUIThread::notify_simulation_changed() {
    simulation_changed = true;
    update_cv.notify_one();
}

void GUIThread::gui_thread_func() {
    // GUI is already initialized in Application::initialize
    // init_gui_components(window, glsl_version); // Removed to avoid double initialization
    
    // Mark as initialized
    {
        std::lock_guard<std::mutex> lock(gui_mutex);
        initialized = true;
    }
    init_cv.notify_all();
    
    // Main render loop
    while (!stop_flag.load() && !glfwWindowShouldClose(window)) {
        // Process pending logs
        {
            std::lock_guard<std::mutex> lock(gui_mutex);
            for (const auto& log : pending_logs) {
                add_log(log);
            }
            pending_logs.clear();
        }
        
        // Only render at a reasonable framerate (60 FPS is more than enough for a UI)
        auto frame_start = std::chrono::steady_clock::now();
        
        // NOTE: GLFW calls moved to main thread
        // We don't call glfwPollEvents() or glfwWindowShouldClose() here
        // These functions should be called from the same thread that created the GLFW context
        
        // NOTE: GUI rendering moved to main thread to avoid OpenGL context issues
        // OpenGL contexts are thread-local, so we've moved rendering to the main thread
        // This thread now only handles data updates and notifications
        
        // Throttle rendering to around 60 FPS
        auto frame_end = std::chrono::steady_clock::now();
        auto frame_time = std::chrono::duration_cast<std::chrono::milliseconds>(frame_end - frame_start).count();
        if (frame_time < 16) { // ~16ms for 60 FPS
            std::this_thread::sleep_for(std::chrono::milliseconds(16 - frame_time));
        }
        
        // Wait for simulation changes or timeout
        if (!simulation_changed.load() && !stop_flag.load()) {
            std::unique_lock<std::mutex> lock(gui_mutex);
            update_cv.wait_for(lock, std::chrono::milliseconds(16), 
                              [this]() { return simulation_changed.load() || stop_flag.load(); });
            simulation_changed = false;
        }
    }
    
    // GUI cleanup moved to main thread (Application::shutdown)
    // We don't call shutdown_gui_components() here as it could have OpenGL context issues
}
