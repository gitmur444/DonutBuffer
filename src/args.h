#pragma once
#include <vector>
#include <string>

// Command-line arguments wrapper
struct Args {
    std::vector<std::string> original; // All argv[] as strings
    std::vector<std::string> unknown;  // Unparsed/unknown arguments
};
