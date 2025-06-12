#include "gui.h" // Main header for GUI and simulation logic
#include "imgui.h" // For ImVec4, ImGui::GetDrawData
#include "application.h"
#include "gui.h" // For add_log, though Application uses it internally. Could be for main-level logging if needed.
#include <iostream> // For std::cerr in case of critical app init failure

int main(int, char**) {
    // Optional: Initial log entry from main itself
    // add_log("Application starting from main()..."); // add_log is available via gui.h

    Application app;

    if (!app.initialize(1280, 720, "Ring Buffer GUI - Refactored")) {
        // Application::initialize already logs errors using add_log.
        // std::cerr is for cases where logging itself might not be set up or visible.
        std::cerr << "FATAL: Application initialization failed. Check log for details." << std::endl;
        // Potentially call a simple platform-specific message box here if desired
        return -1;
    }

    app.run_main_loop();
    
    app.shutdown(); // Explicitly call shutdown

    // add_log("Application exited gracefully from main()."); // Log final exit
    return 0;
}
