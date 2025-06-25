#include "flags.h"
#include <cstring>
#include <vector>
#include <string>

AppFlags parse_flags(int argc, char** argv) {
    AppFlags flags;
    for (int i = 1; i < argc; ++i) {
        flags.args.original.emplace_back(argv[i]);
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--nogui") {
            flags.nogui = true;
        } else if (arg == "--mutex-vs-lockfree") {
            flags.mutex_vs_lockfree = true;
        } else if (arg == "--concurrent-vs-lockfree") {
            flags.concurrent_vs_lockfree = true;
        } else if (arg.rfind("--buffer-type=", 0) == 0) {
            flags.buffer_config.buffer_type = arg.substr(14);
        } else if (arg.rfind("--producers=", 0) == 0) {
            flags.buffer_config.producer_count = std::stoi(arg.substr(12));
        } else if (arg.rfind("--consumers=", 0) == 0) {
            flags.buffer_config.consumer_count = std::stoi(arg.substr(12));
        } else if (arg.rfind("--buffer-size_mb=", 0) == 0) {
            flags.buffer_config.buffer_size_mb = std::stoi(arg.substr(16));
        } else if (arg.rfind("--total-transfer_mb=", 0) == 0) {
            flags.buffer_config.total_transfer_mb = std::stoull(arg.substr(20));
        } else {
            flags.args.unknown.emplace_back(argv[i]);
        }
    }
    return flags;
}

