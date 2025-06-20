#pragma once
#include <vector>
#include <cstring>
#include "args.h"

// Abstract base class for all experiments
class ExperimentBase {
public:
    virtual ~ExperimentBase() = default;
    // Run the experiment
    virtual void run() = 0;
    // Return the CLI flag for this experiment
    virtual const char* flag() const = 0;
    // Register experiment instance
    static void register_experiment(ExperimentBase* exp);
    // Try to find and run experiment by unknown CLI args
    static bool try_run_experiment(const Args& args);
protected:
    // Access to registry of all experiments
    static std::vector<ExperimentBase*>& registry();
};
