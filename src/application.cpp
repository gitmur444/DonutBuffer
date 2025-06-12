#include "application.h"
#include "ring_buffer.h"
#include "simulation_manager.h"
#include "gui.h"
#include "performance_history.h"
#include <GLFW/glfw3.h> // For glfwWindowShouldClose, glfwPollEvents, glfwSwapBuffers, glfwDestroyWindow, glfwTerminate, glfwGetFramebufferSize
#include "imgui.h" // For ImGui::GetDrawData, ImVec4
#include "../imgui_backends/imgui_impl_opengl3.h" // For ImGui_ImplOpenGL3_RenderDrawData
#include <iostream> // For std::cerr (though gui.h's add_log is preferred)
#include <memory> // For std::unique_ptr

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
    gui_events::on_stop_simulation_request = [this]() {
        this->handle_stop_simulation_request();
    };

    initialized = true;
    add_log("Application initialized successfully.");
    return true;
}

void Application::run_main_loop() {
    if (!initialized) {
        add_log("ERROR: Application not initialized. Cannot run main loop.");
        return;
    }
    if (!window) {
        add_log("ERROR: Window is null. Cannot run main loop.");
        return;
    }

    add_log("Starting main loop...");
    ImVec4 clear_color = ImVec4(0.10f, 0.10f, 0.10f, 1.00f); // Более темный фон для лучшего внешнего вида

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        // Обновляем состояние GUI перед отрисовкой
        if (simulationManager) {
            set_gui_simulation_active_status(simulationManager->is_active());
            set_gui_buffer_stats(simulationManager->get_buffer_item_count(), simulationManager->get_buffer_capacity());
            
            // Обновляем информацию о скорости работы буфера
            if (simulationManager->is_active()) {
                double producer_speed = simulationManager->get_producer_speed();
                double consumer_speed = simulationManager->get_consumer_speed();
                
                set_gui_speed_stats(
                    producer_speed,
                    consumer_speed,
                    simulationManager->get_total_produced(),
                    simulationManager->get_total_consumed()
                );
                
                // Добавляем точку в историю производительности
                g_performance_history.add_data_point(producer_speed, consumer_speed);
            }
        } else {
            set_gui_simulation_active_status(false);
            set_gui_buffer_stats(0, 0);
            set_gui_speed_stats(0.0, 0.0, 0, 0);
        }

        // Очищаем буфер перед отрисовкой
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(clear_color.x, clear_color.y, clear_color.z, clear_color.w);
        glClear(GL_COLOR_BUFFER_BIT);
        
        // Отрисовываем GUI фрейм - включает ImGui::NewFrame(), рендеринг UI и ImGui::Render()
        render_gui_frame(); 
        
        // Отрисовываем данные ImGui в основном окне
        // Обратите внимание, что функция render_gui_frame уже вызывает ImGui::UpdatePlatformWindows() и ImGui::RenderPlatformWindowsDefault()
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
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

    shutdown_gui_components(); 

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
    
    // Ensure any previous run (if stop was requested but not fully joined) is cleaned up.
    // SimulationManager::join_threads() is safe to call even if no threads are joinable.
    add_log("Application: Ensuring previous simulation threads are joined...");
    simulationManager->join_threads(); 

    add_log("Application: Resetting simulation buffer...");
    simulationManager->reset_buffer();

    add_log("Application: Configuring simulation with P:" + std::to_string(producers) + 
              " C:" + std::to_string(consumers) + " BS:" + std::to_string(buffer_size));
    simulationManager->configure(producers, consumers, buffer_size);

    add_log("Application: Starting simulation...");
    simulationManager->start();
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
