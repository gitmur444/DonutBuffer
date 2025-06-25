#include "flags.h"
#include <cstring>
#include <vector>
#include <string>

AppFlags parse_flags(int argc, char** argv) {
    AppFlags flags;
    // Fill all original arguments
    for (int i = 1; i < argc; ++i) {
        flags.args.original.emplace_back(argv[i]);
    }
    // Parse known flags and collect unknown
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (strcmp(argv[i], "--nogui") == 0) {
            flags.nogui = true;
        } else if (arg.rfind("--type=", 0) == 0) {
            flags.type = arg.substr(7);
        } else if (arg.rfind("--producers=", 0) == 0) {
            flags.producers = std::stoi(arg.substr(12));
        } else if (arg.rfind("--consumers=", 0) == 0) {
            flags.consumers = std::stoi(arg.substr(12));
        } else {
            flags.args.unknown.emplace_back(argv[i]);
        }
    }
    return flags;
}

