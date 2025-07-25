#pragma once
#include <string>
#include "args.h"
#include "ring_buffer_config.h"

struct AppFlags {
    bool nogui = true;
    bool mutex_vs_lockfree = false;
    bool concurrent_vs_lockfree = false;
    std::string type = "mutex";
    int producers = 1;
    int consumers = 1;
    RingBufferConfig buffer_config;
    Args args;
};

AppFlags parse_flags(int argc, char** argv);
