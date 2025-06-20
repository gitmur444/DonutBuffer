cmake_minimum_required(VERSION 3.20) # Increased for better C++20 module support
set(CMAKE_VERBOSE_MAKEFILE ON) # Show full compile commands
project(DonutBufferApp LANGUAGES CXX C)

set(CMAKE_CXX_EXTENSIONS OFF) # Disable GNU extensions

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_SCAN_FOR_MODULES ON) # Enable module dependency scanning


# --- Dear ImGui --- 
# ImGui source files are in 'imgui/' subdirectory.
# ImGui backend files are in 'imgui_backends/' subdirectory.
find_package(glfw3 REQUIRED)
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
set_property(TARGET imgui PROPERTY CXX_SCAN_FOR_MODULES OFF)

# --- GLAD --- 
# GLAD files are in 'glad/src/' and 'glad/include/'
add_library(glad glad/src/glad.c)
target_include_directories(glad PUBLIC glad/include)
set_property(TARGET glad PROPERTY CXX_SCAN_FOR_MODULES OFF)

# --- GLFW --- 


# --- OpenGL --- 
find_package(OpenGL REQUIRED)

# --- Threads --- 
find_package(Threads REQUIRED)

# --- Main Executable --- 
# --- Source Files ---
file(GLOB_RECURSE CXX_MODULE_INTERFACE_FILES CONFIGURE_DEPENDS
    "${PROJECT_SOURCE_DIR}/src/*.ixx"
    "${PROJECT_SOURCE_DIR}/src/*/*.ixx"
)

file(GLOB_RECURSE CXX_MODULE_IMPLEMENTATION_FILES_ALL CONFIGURE_DEPENDS
    "${PROJECT_SOURCE_DIR}/src/*.cpp"
    "${PROJECT_SOURCE_DIR}/src/*/*.cpp"
)

# Exclude main.cpp from implementation files as it's handled separately
list(FILTER CXX_MODULE_IMPLEMENTATION_FILES_ALL EXCLUDE REGEX ".*/main\\.cpp$")
set(CXX_MODULE_IMPLEMENTATION_FILES ${CXX_MODULE_IMPLEMENTATION_FILES_ALL})

# --- Main Executable ---
add_executable(DonutBufferApp "") # Initialize with empty

target_sources(DonutBufferApp
    PRIVATE
        "${PROJECT_SOURCE_DIR}/src/main.cpp"
        ${CXX_MODULE_IMPLEMENTATION_FILES}
        # External sources (ImGui, GLAD) are added as libraries, so not needed here directly
    PUBLIC
        FILE_SET CXX_MODULES BASE_DIRS "${PROJECT_SOURCE_DIR}/src" FILES ${CXX_MODULE_INTERFACE_FILES}
)

# Add module-specific compile options for DonutBufferApp target
if (CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES "AppleClang")
    message(STATUS "Clang/AppleClang detected.")
elseif (CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    message(STATUS "GCC detected.")
else()
    message(WARNING "Compiler not detected as Clang or GCC. C++20 module flags may not be correctly set for DonutBufferApp.")
endif()

# Link libraries
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

# For macOS, ensure the executable is bundled if needed
if(APPLE)
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
message(STATUS "2. Dear ImGui source files in 'donut_buffer_gui/imgui/' directory.")
message(STATUS "3. Dear ImGui backend files (imgui_impl_*.cpp/h) in 'donut_buffer_gui/' directory.")
message(STATUS "4. GLAD files (glad.c, glad.h, KHR) in 'donut_buffer_gui/glad/' subdirectories.")
message(STATUS "2. Dear ImGui source files in 'ring_buffer_gui/imgui/' directory.")
message(STATUS "3. Dear ImGui backend files (imgui_impl_*.cpp/h) in 'ring_buffer_gui/' directory.")
message(STATUS "4. GLAD files (glad.c, glad.h, KHR) in 'ring_buffer_gui/glad/' subdirectories.")
message(STATUS "---------------------------------------------------------------------")
