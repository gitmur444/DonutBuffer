#pragma once
#include <string>
#include "args.h"

struct AppFlags {
    bool nogui = false;
    Args args;
};

AppFlags parse_flags(int argc, char** argv);
