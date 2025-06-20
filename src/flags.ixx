export module flags;

import args; // Import the Args struct from its own module
#include <string> // For std::string if used directly in AppFlags or parse_flags, otherwise can be removed if only args.ixx needs it.

export struct AppFlags {
    bool nogui = false;
    Args args; // Use the imported Args struct
};

export AppFlags parse_flags(int argc, char** argv);
