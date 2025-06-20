#include "application.h" // Assuming Application class is defined here
#include "gui/gui.h"       // Assuming GUI related functions/classes are here
#include "flags.h"         // Assuming AppFlags and parse_flags are defined here
#include "experiments/experiment_base.h" // Assuming ExperimentBase is here

#include "imgui.h" // For ImVec4, ImGui::GetDrawData. This is a C library, so it remains an include.
#include <iostream> // For std::cerr in case of critical app init failure
#include <filesystem>
#include <cstdlib>

int main(int argc, char** argv) {
    AppFlags flags = parse_flags(argc, argv);
    // Run experiment if requested, then exit
    if (ExperimentBase::try_run_experiment(flags.args)) {
        return 0;
    }

    if (flags.nogui) {
        std::cout << "Running in --nogui mode (no GUI, no simulation logic implemented yet)" << std::endl;
        // Здесь можно добавить headless-режим или тесты без GUI
        return 0;
    }
    Application app;
    if (!app.initialize(1280, 720, "Ring Buffer GUI - Refactored")) {
        std::cerr << "FATAL: Application initialization failed. Check log for details." << std::endl;
        return -1;
    }
    app.run_main_loop();
    app.shutdown();
    return 0;
}
