export module experiments.experiment_base;

import args; // For Args struct used in try_run_experiment

#include <vector>   // For std::vector used in registry
#include <string>   // For std::string if needed (flag() returns const char*)
#include <cstring>  // For strcmp or similar if used in implementation of try_run_experiment
                    // Consider <string_view> for modern C++ comparisons if applicable

// Abstract base class for all experiments
export class ExperimentBase {
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
