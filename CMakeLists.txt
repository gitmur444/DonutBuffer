cmake_minimum_required(VERSION 3.10)
project(DonutBufferApp LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# --- Dear ImGui --- 
# ImGui source files are in 'imgui/' subdirectory.
# ImGui backend files are in 'imgui_backends/' subdirectory.
find_package(glfw3 QUIET)

if(glfw3_FOUND)
    add_library(imgui
        imgui/imgui.cpp
        imgui/imgui_draw.cpp
        imgui/imgui_tables.cpp
        imgui/imgui_widgets.cpp
        imgui_backends/imgui_impl_glfw.cpp    # Updated path
        imgui_backends/imgui_impl_opengl3.cpp # Updated path
    )
    target_include_directories(imgui PUBLIC
        imgui/          # For imgui.h, imgui_internal.h etc.
        glad/include    # For glad.h needed by imgui_impl_opengl3.cpp
    )
    target_link_libraries(imgui PUBLIC glfw glad)
    set(GUI_AVAILABLE TRUE)
else()
    message(WARNING "GLFW3 not found. GUI components will be disabled.")
    set(GUI_AVAILABLE FALSE)
endif()

# --- GLAD --- 
# GLAD files are in 'glad/src/' and 'glad/include/'
add_library(glad glad/src/glad.c)
target_include_directories(glad PUBLIC glad/include)

# --- GLFW --- 


# --- OpenGL --- 
if(GUI_AVAILABLE)
    find_package(OpenGL REQUIRED)
endif()

# --- Threads --- 
find_package(Threads REQUIRED)

# --- Google Test ---
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG v1.14.0
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# --- Main Executable --- 
if(GUI_AVAILABLE)
    add_executable(DonutBufferApp
        src/main.cpp          # Updated path and added files
        src/simulation_manager.cpp # Added
        src/application.cpp      # Added
        src/performance_history.cpp # Added performance history
        src/gui/gui.cpp           # GUI implementation
        src/gui/gui_thread.cpp    # GUI thread implementation
        src/flags.cpp         # Flags parser implementation
        src/ringbuffer/mutex_ring_buffer.cpp # MutexRingBuffer implementation
        src/ringbuffer/lockfree_ring_buffer.cpp # LockFreeRingBuffer implementation
        src/experiments/experiment_base.cpp
        src/experiments/experiment_base.h
        src/experiments/concurrent_vs_lockfree_experiment.cpp
        src/experiments/concurrent_vs_lockfree_experiment.h
        src/experiments/mutex_vs_lockfree_experiment.cpp
        src/experiments/mutex_vs_lockfree_experiment.h
    )
    
    target_link_libraries(DonutBufferApp
        PRIVATE
        imgui
        glad
        glfw
        ${OPENGL_LIBRARIES}
        Threads::Threads
    )

    # Specify include directories for the main target (${PROJECT_NAME})
    target_include_directories(DonutBufferApp PUBLIC
        src/                # Added: For gui.h, ring_buffer.h
        imgui/              # For imgui.h (used by gui.cpp, main.cpp)
        glad/include        # For glad.h (used by main.cpp, gui.cpp)
        imgui_backends/     # Added: For imgui_impl_glfw.h, imgui_impl_opengl3.h (used by gui.cpp, main.cpp)
    )
else()
    message(STATUS "GUI components disabled - DonutBufferApp will not be built")
endif()

# Simple CLI runner for ring buffer benchmarks
add_executable(buffer_runner
    src/buffer_runner.cpp
    src/ringbuffer/mutex_ring_buffer.cpp
    src/ringbuffer/lockfree_ring_buffer.cpp
)
target_link_libraries(buffer_runner PRIVATE Threads::Threads)
target_include_directories(buffer_runner PUBLIC src/)

add_subdirectory(tests)

# For macOS, ensure the executable is bundled if needed
if(APPLE AND GUI_AVAILABLE)
    set(CMAKE_MACOSX_BUNDLE_GUI_IDENTIFIER "com.example.donutbufferapp")
    set(CMAKE_MACOSX_BUNDLE_BUNDLE_NAME "DonutBufferApp")
    set_target_properties(DonutBufferApp PROPERTIES MACOSX_BUNDLE TRUE) # Ensure .app bundle is created
    target_link_libraries(DonutBufferApp PRIVATE "-framework Cocoa" "-framework IOKit" "-framework CoreVideo" "-framework OpenGL") # Explicitly link required frameworks on macOS
    # If you have an Info.plist, add it here:
    # set_target_properties(DonutBufferApp PROPERTIES MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/Info.plist)
endif()

message(STATUS "---------------------------------------------------------------------")
message(STATUS "Project: DonutBufferApp")
message(STATUS "To build this project, ensure you have setup the dependencies:")
message(STATUS "1. GLFW installed (e.g., 'brew install glfw' on macOS).")
message(STATUS "2. Dear ImGui source files are in the 'imgui/' directory.")
message(STATUS "3. Dear ImGui backend files (imgui_impl_*.cpp/h) are in the 'imgui_backends/' directory.")
message(STATUS "4. GLAD files (glad.c, glad.h, KHR) are in the 'glad/' directory.")
message(STATUS "---------------------------------------------------------------------")
