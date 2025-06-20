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
        if (strcmp(argv[i], "--nogui") == 0) {
            flags.nogui = true;
        } else {
            flags.args.unknown.emplace_back(argv[i]);
        }
    }
    return flags;
}

