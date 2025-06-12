#include "gui.h"
#include "ring_buffer.h" // For RingBuffer class usage
#include "performance_history.h" // For performance history tracking

#include "imgui.h"
#include "../imgui_backends/imgui_impl_glfw.h"
#include "../imgui_backends/imgui_impl_opengl3.h"

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include <iostream>
#include <sstream>
#include <iomanip> // For std::setfill, std::setw
#include <chrono>
#include <cstdlib>
#include <ctime>
#include <string>
#include <vector>
#include <thread>
#include <memory>
#include <list>
#include <mutex>
#include <atomic> // Required for std::atomic

// --- Configuration Constants Definitions ---
const int MAX_BUFFER_SIZE = 100;
const int MAX_PRODUCERS = 10;
const int MAX_CONSUMERS = 10;
const size_t MAX_LOG_ENTRIES = 100;

// --- Global State Definitions (related to GUI) ---
// GUI specific state (used to configure SimulationManager via callbacks)
// Callbacks for GUI actions
namespace gui_events {
    std::function<void(int, int, int)> on_start_simulation_request;
    std::function<void()> on_stop_simulation_request;
}

// Internal GUI state, updated by Application via setter functions
static bool current_gui_simulation_is_active = false;
static size_t current_gui_buffer_item_count = 0;
static size_t current_gui_buffer_capacity = 0;

// GUI specific state (used to configure SimulationManager)
int num_producers_gui = 2;
int num_consumers_gui = 1;
int buffer_size_gui = 10;

// Speed measurement variables
double producer_speed_gui = 0.0;
double consumer_speed_gui = 0.0;
size_t total_produced_gui = 0;
size_t total_consumed_gui = 0;

// Performance graph controls
bool show_producer_graph = true;
bool show_consumer_graph = true;

// Logging utilities remain global for now, add_log is passed to SimulationManager
std::mutex log_mutex;
std::list<std::string> event_log;

// --- GLFW Error Callback ---
void glfw_error_callback(int error, const char* description) {
    std::cerr << "GLFW Error " << error << ": " << description << std::endl;
}

// --- Platform and Window Initialization ---
// Initializes GLFW, creates a window, and initializes GLAD.
// Returns true on success, false on failure.
// Outputs the created GLFWwindow* and the determined GLSL version string.
bool initialize_platform_and_window(GLFWwindow*& out_window, const char*& out_glsl_version, int width, int height, const char* title) {
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return false;
    }

    // Decide GL+GLSL versions
#if defined(IMGUI_IMPL_OPENGL_ES2)
    // GL ES 2.0 + GLSL 100
    out_glsl_version = "#version 100";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
#elif defined(__APPLE__)
    // GL 3.2 + GLSL 150
    out_glsl_version = "#version 150";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3); // Consistent with previous setup
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // Required on Mac
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // Required on Mac
#else
    // GL 3.0 + GLSL 130
    out_glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // Optional
    //glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // Optional
#endif

    out_window = glfwCreateWindow(width, height, title, NULL, NULL);
    if (out_window == NULL) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return false;
    }
    glfwMakeContextCurrent(out_window);
    glfwSwapInterval(1); // Enable vsync

    // Initialize GLAD
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Failed to initialize GLAD" << std::endl;
        glfwDestroyWindow(out_window); // Clean up window before terminating
        glfwTerminate();
        return false;
    }
    add_log("Platform and window initialized successfully."); // Added log message
    return true;
}

// --- GUI State Update Functions (called by Application) ---
void set_gui_simulation_active_status(bool is_active) {
    current_gui_simulation_is_active = is_active;
}

void set_gui_buffer_stats(size_t item_count, size_t capacity) {
    current_gui_buffer_item_count = item_count;
    current_gui_buffer_capacity = capacity;
}

void set_gui_speed_stats(double producer_speed, double consumer_speed, size_t total_produced, size_t total_consumed) {
    producer_speed_gui = producer_speed;
    consumer_speed_gui = consumer_speed;
    total_produced_gui = total_produced;
    total_consumed_gui = total_consumed;
}

// --- Logging ---
// Definition of add_log remains, it's used by GUI and passed to SimulationManager
void add_log(const std::string& message) {
    std::lock_guard<std::mutex> lock(log_mutex);
    auto now = std::chrono::system_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    char time_buf[20];
    // Check if std::localtime returns nullptr
    std::tm* local_time_tm = std::localtime(&t);
    if (local_time_tm) {
        std::strftime(time_buf, sizeof(time_buf), "%H:%M:%S", local_time_tm);
    } else {
        // Fallback if localtime fails
        std::snprintf(time_buf, sizeof(time_buf), "??:??:??");
    }
    std::stringstream ss;
    ss << time_buf << "." << std::setfill('0') << std::setw(3) << ms.count() << ": " << message;
    
    event_log.push_back(ss.str());
    if (event_log.size() > MAX_LOG_ENTRIES) {
        event_log.pop_front();
    }
}

// --- GUI Related Functions ---
void init_gui_components(GLFWwindow* window, const char* glsl_version) {
    // Setup ImGui binding
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    (void)io;
    
    // Set larger font size
    ImFontConfig font_config;
    font_config.SizePixels = 18.0f; // Increase default font size
    io.Fonts->AddFontDefault(&font_config);

    // Setup Dear ImGui style
    ImGui::StyleColorsDark();
    
    // Increase UI element sizes
    ImGuiStyle& style = ImGui::GetStyle();
    style.WindowRounding = 0.0f;
    style.FramePadding = ImVec2(8, 6);      // Larger padding around controls
    style.ItemSpacing = ImVec2(12, 8);      // More space between items
    style.TouchExtraPadding = ImVec2(4, 4); // Extra padding for touch input
    style.IndentSpacing = 25.0f;            // Wider indentation
    style.ScrollbarSize = 18.0f;            // Wider scrollbars
    style.GrabMinSize = 18.0f;              // Wider slider grab
    style.ButtonTextAlign = ImVec2(0.5f, 0.5f); // Center button text
    
    // Larger elements for better visibility
    style.FrameRounding = 4.0f;             // Rounded frames
    style.GrabRounding = 4.0f;              // Rounded slider grab
    style.TabRounding = 4.0f;               // Rounded tabs

    // Initialize imgui for opengl and glfw
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    
    add_log("GUI components initialized with larger font and controls.");
    add_log("OpenGL Vendor: " + std::string((const char*)glGetString(GL_VENDOR)));
    add_log("OpenGL Renderer: " + std::string((const char*)glGetString(GL_RENDERER)));
    add_log("OpenGL Version: " + std::string((const char*)glGetString(GL_VERSION)));
    add_log("GLSL Version: " + std::string(glsl_version));
}

void render_gui_frame() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    // Создаем полноэкранное окно без заголовка
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 0.0f);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
    
    ImGuiWindowFlags window_flags = ImGuiWindowFlags_NoTitleBar | 
                                    ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoResize | 
                                    ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoBringToFrontOnFocus | 
                                    ImGuiWindowFlags_NoNavFocus;
    
    ImGui::Begin("RingBufferGUI", nullptr, window_flags);
    ImGui::PopStyleVar(2);
    
    // Отображаем информацию о производительности
    ImGui::Text("Application average %.3f ms/frame (%.1f FPS)", 1000.0f / ImGui::GetIO().Framerate, ImGui::GetIO().Framerate);
    
    ImGui::Separator();
    ImGui::Text("Configuration:");
    
    ImGui::BeginDisabled(current_gui_simulation_is_active);
    ImGui::SliderInt("Producers", &num_producers_gui, 1, MAX_PRODUCERS, "%d");
    ImGui::SliderInt("Consumers", &num_consumers_gui, 1, MAX_CONSUMERS, "%d");
    ImGui::SliderInt("Buffer Size", &buffer_size_gui, 1, MAX_BUFFER_SIZE, "%d");
    ImGui::EndDisabled();

    if (current_gui_simulation_is_active) {
        if (ImGui::Button("Stop Simulation")) {
            if (gui_events::on_stop_simulation_request) {
                gui_events::on_stop_simulation_request();
            } else {
                add_log("WARN: Stop simulation request not handled (callback not set).");
            }
        }
    } else {
        if (ImGui::Button("Start Simulation")) {
            if (gui_events::on_start_simulation_request) {
                gui_events::on_start_simulation_request(num_producers_gui, num_consumers_gui, buffer_size_gui);
            } else {
                add_log("WARN: Start simulation request not handled (callback not set).");
            }
        }
    }

    ImGui::Separator();
    ImGui::Text("Buffer Status:");
    float buffer_fill_ratio = (current_gui_buffer_capacity > 0) ? 
                              static_cast<float>(current_gui_buffer_item_count) / current_gui_buffer_capacity : 0.0f;
    ImGui::ProgressBar(buffer_fill_ratio, ImVec2(0.0f, 0.0f));
    ImGui::Text("Items: %zu / %zu", current_gui_buffer_item_count, current_gui_buffer_capacity);
    
    ImGui::Separator();
    ImGui::Text("Speed Metrics:");
    ImGui::Text("Producer Speed: %.2f items/sec", producer_speed_gui);
    ImGui::Text("Consumer Speed: %.2f items/sec", consumer_speed_gui);
    ImGui::Text("Total Produced: %zu items", total_produced_gui);
    ImGui::Text("Total Consumed: %zu items", total_consumed_gui);
    
    // Speedometer visualization
    const float max_speed = std::max(producer_speed_gui, consumer_speed_gui) * 1.2f; // 20% headroom
    if (max_speed > 0) {
        ImGui::Text("Producer Speedometer:");
        char producer_label[32];
        snprintf(producer_label, sizeof(producer_label), "%.2f items/sec", producer_speed_gui);
        ImGui::ProgressBar(static_cast<float>(producer_speed_gui) / max_speed, ImVec2(0.0f, 0.0f), producer_label);
        
        ImGui::Text("Consumer Speedometer:");
        char consumer_label[32];
        snprintf(consumer_label, sizeof(consumer_label), "%.2f items/sec", consumer_speed_gui);
        ImGui::ProgressBar(static_cast<float>(consumer_speed_gui) / max_speed, ImVec2(0.0f, 0.0f), consumer_label);
    }
    
    // Performance History Graph
    ImGui::Separator();
    ImGui::Text("Performance History Graph");
    ImGui::Checkbox("Show Producer", &show_producer_graph);
    ImGui::SameLine();
    ImGui::Checkbox("Show Consumer", &show_consumer_graph);
    ImGui::SameLine();
    if (ImGui::Button("Clear History")) {
        g_performance_history.clear();
    }

    // Graph area
    if (ImGui::BeginChild("GraphRegion", ImVec2(0, 200), true)) {
        // Get graph data
        const auto& producer_history = g_performance_history.get_producer_history();
        const auto& consumer_history = g_performance_history.get_consumer_history();
        const auto& run_markers = g_performance_history.get_run_markers();
        
        if (!producer_history.empty()) {
            ImDrawList* draw_list = ImGui::GetWindowDrawList();
            
            // Calculate graph area dimensions
            const ImVec2 graph_size = ImGui::GetContentRegionAvail();
            const ImVec2 canvas_pos = ImGui::GetCursorScreenPos();
            const ImVec2 canvas_size = graph_size;
            
            // Border around the graph
            draw_list->AddRect(canvas_pos, 
                              ImVec2(canvas_pos.x + canvas_size.x, canvas_pos.y + canvas_size.y), 
                              ImGui::GetColorU32(ImGuiCol_Border));
            
            // Maximum speed for scaling
            float max_display_speed = g_performance_history.get_max_speed() * 1.1f; // 10% margin
            if (max_display_speed < 1.0f) max_display_speed = 1.0f; // Minimum scale
            
            // Draw run separators
            for (const auto& marker : run_markers) {
                if (marker > 0 && marker < static_cast<int>(producer_history.size())) {
                    float x_pos = canvas_pos.x + (marker / static_cast<float>(producer_history.size() - 1)) * canvas_size.x;
                    draw_list->AddLine(
                        ImVec2(x_pos, canvas_pos.y),
                        ImVec2(x_pos, canvas_pos.y + canvas_size.y),
                        ImGui::GetColorU32(ImVec4(1.0f, 1.0f, 1.0f, 0.5f)), 
                        1.0f
                    );
                }
            }
            
            // Draw producer graph
            if (show_producer_graph && producer_history.size() > 1) {
                for (size_t i = 0; i < producer_history.size() - 1; i++) {
                    float x1 = canvas_pos.x + (i / static_cast<float>(producer_history.size() - 1)) * canvas_size.x;
                    float y1 = canvas_pos.y + canvas_size.y - (producer_history[i] / max_display_speed) * canvas_size.y;
                    float x2 = canvas_pos.x + ((i + 1) / static_cast<float>(producer_history.size() - 1)) * canvas_size.x;
                    float y2 = canvas_pos.y + canvas_size.y - (producer_history[i + 1] / max_display_speed) * canvas_size.y;
                    
                    draw_list->AddLine(
                        ImVec2(x1, y1),
                        ImVec2(x2, y2),
                        ImGui::GetColorU32(ImVec4(1.0f, 0.4f, 0.4f, 1.0f)), // Red for producers
                        2.0f
                    );
                }
            }
            
            // Draw consumer graph
            if (show_consumer_graph && consumer_history.size() > 1) {
                for (size_t i = 0; i < consumer_history.size() - 1; i++) {
                    float x1 = canvas_pos.x + (i / static_cast<float>(consumer_history.size() - 1)) * canvas_size.x;
                    float y1 = canvas_pos.y + canvas_size.y - (consumer_history[i] / max_display_speed) * canvas_size.y;
                    float x2 = canvas_pos.x + ((i + 1) / static_cast<float>(consumer_history.size() - 1)) * canvas_size.x;
                    float y2 = canvas_pos.y + canvas_size.y - (consumer_history[i + 1] / max_display_speed) * canvas_size.y;
                    
                    draw_list->AddLine(
                        ImVec2(x1, y1),
                        ImVec2(x2, y2),
                        ImGui::GetColorU32(ImVec4(0.4f, 0.8f, 0.4f, 1.0f)), // Green for consumers
                        2.0f
                    );
                }
            }
            
            // Axis labels
            char label[64];
            snprintf(label, sizeof(label), "Max: %.2f items/sec", max_display_speed);
            draw_list->AddText(ImVec2(canvas_pos.x + 5, canvas_pos.y + 5), 
                              ImGui::GetColorU32(ImGuiCol_Text), label);
                              
            // Legend
            float legend_y = canvas_pos.y + canvas_size.y - 20;
            if (show_producer_graph) {
                draw_list->AddLine(
                    ImVec2(canvas_pos.x + 5, legend_y),
                    ImVec2(canvas_pos.x + 25, legend_y),
                    ImGui::GetColorU32(ImVec4(1.0f, 0.4f, 0.4f, 1.0f)),
                    2.0f
                );
                draw_list->AddText(
                    ImVec2(canvas_pos.x + 30, legend_y - 7),
                    ImGui::GetColorU32(ImGuiCol_Text),
                    "Producer"
                );
            }
            
            if (show_consumer_graph) {
                float offset = show_producer_graph ? 120.0f : 0.0f;
                draw_list->AddLine(
                    ImVec2(canvas_pos.x + 5 + offset, legend_y),
                    ImVec2(canvas_pos.x + 25 + offset, legend_y),
                    ImGui::GetColorU32(ImVec4(0.4f, 0.8f, 0.4f, 1.0f)),
                    2.0f
                );
                draw_list->AddText(
                    ImVec2(canvas_pos.x + 30 + offset, legend_y - 7),
                    ImGui::GetColorU32(ImGuiCol_Text),
                    "Consumer"
                );
            }
        }
        else {
            // If no data available
            const ImVec2 graph_size = ImGui::GetContentRegionAvail();
            ImGui::SetCursorPosY(ImGui::GetCursorPosY() + graph_size.y / 2 - 10);
            ImGui::SetCursorPosX(ImGui::GetCursorPosX() + graph_size.x / 2 - 120);
            ImGui::Text("No performance data available yet");
        }
        
        ImGui::EndChild();
    }
    
    ImGui::Separator();
    ImGui::Text("Event Log:");
    ImGui::BeginChild("LogRegion", ImVec2(0, 150), true, ImGuiWindowFlags_HorizontalScrollbar);
    {
        std::lock_guard<std::mutex> lock(log_mutex); 
        for (const auto& entry : event_log) {
            ImGui::TextUnformatted(entry.c_str());
        }
        if (ImGui::GetScrollY() >= ImGui::GetScrollMaxY() && ImGui::GetScrollMaxY() > 0) { 
            ImGui::SetScrollHereY(1.0f);
        }
    }
    ImGui::EndChild();
    
    ImGui::End(); // End "RingBufferGUI" window

    ImGui::Render();
}

void shutdown_gui_components() {
    add_log("Shutting down GUI components...");

    // SimulationManager cleanup is now handled by Application class

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    add_log("ImGui components shut down.");
}
