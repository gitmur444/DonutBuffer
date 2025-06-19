#include "application.h"
#include "performance_history.h"
#include "simulation_manager.h"
#include "gui.h"
#include "gui_thread.h"
#include <GLFW/glfw3.h> // For glfwWindowShouldClose, glfwPollEvents, glfwSwapBuffers, glfwDestroyWindow, glfwTerminate, glfwGetFramebufferSize
#include "imgui.h" // For ImGui::GetDrawData, ImVec4
#include "../imgui_backends/imgui_impl_opengl3.h" // For ImGui_ImplOpenGL3_RenderDrawData
#include <iostream> // For std::cerr (though gui.h's add_log is preferred)
#include <memory> // For std::shared_ptr
#include <thread> // For std::this_thread
#include <chrono> // For std::chrono

Application::Application() : window(nullptr), initialized(false), shutdown_called(false), simulationManager(nullptr) {
    // Constructor can call add_log if it's made accessible or if Application takes a logger
    // For now, keep it simple. add_log is available globally via gui.h
    add_log("Application instance created.");
}

Application::~Application() {
    if (initialized && !shutdown_called) {
        add_log("Application destructor: performing shutdown...");
        shutdown();
    }
    add_log("Application instance destroyed.");
}

bool Application::initialize(int width, int height, const char* title) {
    if (initialized) {
        add_log("Application already initialized.");
        return true;
    }
    add_log("Application initializing...");

    const char* glsl_version = nullptr; // Will be set by initialize_platform_and_window

    if (!initialize_platform_and_window(window, glsl_version, width, height, title)) {
        add_log("ERROR: Failed to initialize platform and window.");
        // Error message is printed within initialize_platform_and_window
        return false;
    }

    // init_gui_components now also initializes SimulationManager via sim_manager_ptr
    init_gui_components(window, glsl_version);
    add_log("GUI components initialized.");

    // Initialize SimulationManager
    add_log("Application: Initializing SimulationManager...");
    simulationManager = std::make_unique<SimulationManager>(::add_log); // Use global GUI logger
    if (simulationManager) {
        // Optionally configure with default values from gui.cpp if needed immediately
        // simulationManager->configure(num_producers_gui, num_consumers_gui, buffer_size_gui);
        add_log("Application: SimulationManager created.");
    } else {
        add_log("ERROR: Application: Failed to create SimulationManager!");
    }

    // Setup GUI callbacks
    gui_events::on_start_simulation_request = [this](int p, int c, int bs) {
        this->handle_start_simulation_request(p, c, bs);
    };
    gui_events::on_buffer_impl_changed = [this](int impl) {
        if (simulationManager) {
            simulationManager->set_buffer_type(impl == 0 ? RingBufferType::Custom : RingBufferType::ConcurrentQueue);
            simulationManager->reset_buffer(); // пересоздать буфер, история графика не сбрасывается
            add_log(impl == 0 ? "Application: Switched to Custom RingBuffer" : "Application: Switched to ConcurrentQueue RingBuffer");
        }
    };

    gui_events::on_stop_simulation_request = [this]() {
        this->handle_stop_simulation_request();
    };
    
    // Setup dynamic parameter update callbacks
    gui_events::on_producer_count_update = [this](int count) {
        this->handle_producer_count_update(count);
    };
    gui_events::on_consumer_count_update = [this](int count) {
        this->handle_consumer_count_update(count);
    };
    gui_events::on_buffer_size_update = [this](int size) {
        this->handle_buffer_size_update(size);
    };

    initialized = true;
    add_log("Application initialized successfully.");
    return true;
}

void Application::run_main_loop() {
    if (!initialized || !window) {
        std::cerr << "Application not initialized!" << std::endl;
        return;
    }
    
    add_log("Starting main loop...");
    
    // Initialize GUI thread
    if (!g_gui_thread.init(simulationManager.get(), window)) {
        add_log("ERROR: Failed to initialize GUI thread");
        return;
    }
    
    add_log("GUI thread started successfully");
    
    // Main application loop - now handles all window/rendering operations
    while (!g_gui_thread.should_close()) {
        // Poll for and process events
        glfwPollEvents();
        
        // Check if window should close
        if (glfwWindowShouldClose(window)) {
            g_gui_thread.stop(); // Signal GUI thread to stop
        }
        // Update simulation statistics if we have an active simulation
        if (simulationManager && simulationManager->is_active()) {
            // Update speed measurements
            // Speed updates are now handled internally by SimulationManager
            
            // Get the current speeds
            double producer_speed = simulationManager->get_producer_speed();
            double consumer_speed = simulationManager->get_consumer_speed();
            
            // Calculate average throughput for simplified metric
            double avg_throughput = (producer_speed + consumer_speed) / 2.0;
            
            // Add to performance history with simplified metric
            g_performance_history.add_data_point(avg_throughput);
            
            // Update GUI stats
            set_gui_simulation_active_status(true);
            set_gui_buffer_stats(
                simulationManager->get_buffer_item_count(), 
                simulationManager->get_buffer_capacity()
            );
            set_gui_speed_stats(
                producer_speed,
                consumer_speed,
                simulationManager->get_total_produced(),
                simulationManager->get_total_consumed()
            );
            
            // Notify GUI thread about simulation updates
            g_gui_thread.notify_simulation_changed();
        } else if (simulationManager) {
            // Update stats for inactive simulation
            set_gui_simulation_active_status(false);
            set_gui_buffer_stats(
                simulationManager->get_buffer_item_count(),
                simulationManager->get_buffer_capacity()
            );
            g_gui_thread.notify_simulation_changed();
        } else {
            // No simulation manager
            set_gui_simulation_active_status(false);
            set_gui_buffer_stats(0, 0);
            set_gui_speed_stats(0.0, 0.0, 0, 0);
            g_gui_thread.notify_simulation_changed();
        }
        
        // Render GUI in main thread (where OpenGL context was created)
        render_gui_frame();
        
        // Swap buffers (draw to screen)
        glfwSwapBuffers(window);
        
        // Throttle loop to reasonable framerate
        std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
    }
    
    add_log("Main loop ended.");
}

void Application::shutdown() {
    if (!initialized || shutdown_called) {
        if (shutdown_called) add_log("Shutdown already called.");
        else add_log("Application not initialized or already shut down.");
        return;
    }

    add_log("Application shutting down...");

    // Shutdown SimulationManager first
    if (simulationManager) {
        add_log("Application: Shutting down SimulationManager...");
        if (simulationManager->is_active()) {
            add_log("Application: Requesting simulation stop...");
            simulationManager->request_stop();
        }
        add_log("Application: Joining simulation threads...");
        simulationManager->join_threads();
        simulationManager.reset();
        add_log("Application: SimulationManager released.");
    } else {
        add_log("Application: SimulationManager was not initialized, skipping its shutdown.");
    }

    // Stop GUI thread gracefully
    add_log("Application: Stopping GUI thread...");
    g_gui_thread.stop();
    add_log("Application: GUI thread stopped.");
    
    // Shutdown GUI components
    shutdown_gui_components(); 
    add_log("Application: GUI components shut down.");

    // Cleanup GLFW resources
    if (window) {
        glfwDestroyWindow(window);
        window = nullptr;
    }
    glfwTerminate();
    add_log("GLFW terminated.");

    initialized = false;
    shutdown_called = true;
    add_log("Application shut down complete.");
}

// --- Simulation Control Handlers ---
void Application::handle_start_simulation_request(int producers, int consumers, int buffer_size) {
    add_log("Application: Start simulation requested by GUI.");
    
    if (simulationManager && simulationManager->is_active()) {
        add_log("Application: Simulation is already active. Stopping current simulation before starting a new one.");
        simulationManager->request_stop();
        simulationManager->join_threads();
        add_log("Application: Previous simulation stopped.");
    }
    
    // Add a marker for a new run in the performance history graph
    g_performance_history.mark_new_run();
    
    // Create new simulation manager with requested parameters
    simulationManager = std::make_unique<SimulationManager>(::add_log);
    simulationManager->configure(buffer_size, producers, consumers);
    
    // Start simulation
    simulationManager->start();
    
    // Log the event through the GUI thread
    g_gui_thread.add_log("Started simulation with " + std::to_string(producers) + 
                       " producers and " + std::to_string(consumers) + 
                       " consumers. Buffer size: " + std::to_string(buffer_size));
}

void Application::handle_stop_simulation_request() {
    add_log("Application: Stop simulation requested by GUI.");
    if (!simulationManager) {
        add_log("WARN: Application: SimulationManager is not initialized. Cannot stop simulation.");
        return;
    }

    if (!simulationManager->is_active()) {
        add_log("Application: Simulation is not active. Ignoring stop request.");
        return;
    }

    add_log("Application: Requesting simulation to stop...");
    simulationManager->request_stop();
    
    // Важно - присоединяем потоки, чтобы гарантировать их завершение
    add_log("Application: Joining threads to ensure clean stop...");
    simulationManager->join_threads();
    add_log("Application: All threads joined, simulation stopped.");
}

// Обработчики для динамического изменения параметров
void Application::handle_producer_count_update(int new_count) {
    if (!simulationManager) {
        add_log("ERROR: Cannot update producer count: SimulationManager is null.");
        return;
    }
    
    add_log("Application: Dynamically updating producer count to " + std::to_string(new_count));
    simulationManager->update_producers(new_count);
    
    // Log the change through the GUI thread
    g_gui_thread.add_log("Updated producer count to " + std::to_string(new_count));
}

void Application::handle_consumer_count_update(int new_count) {
    if (!simulationManager) {
        add_log("ERROR: Cannot update consumer count: SimulationManager is null.");
        return;
    }
    
    add_log("Application: Dynamically updating consumer count to " + std::to_string(new_count));
    simulationManager->update_consumers(new_count);
    
    // Log the change through the GUI thread
    g_gui_thread.add_log("Updated consumer count to " + std::to_string(new_count));
}

void Application::handle_buffer_size_update(int new_size) {
    if (!simulationManager) {
        add_log("ERROR: Cannot update buffer size: SimulationManager is null.");
        return;
    }
    
    add_log("Application: Updating buffer size to " + std::to_string(new_size));
    simulationManager->update_buffer_size(new_size);
    
    // Log the change through the GUI thread
    g_gui_thread.add_log("Updated buffer size to " + std::to_string(new_size));
}
