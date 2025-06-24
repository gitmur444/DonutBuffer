#pragma once
#include <string>
#include "args.h"
#include "ring_buffer_config.h"

struct AppFlags {
    bool nogui = true;
    Args args;
    RingBufferConfig buffer_config;
};

AppFlags parse_flags(int argc, char** argv);
