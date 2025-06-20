#include "experiment_base.h"
#include <vector>
#include <cstring>
#include "args.h"

// Static registry for all experiments
std::vector<ExperimentBase*>& ExperimentBase::registry() {
    static std::vector<ExperimentBase*> inst;
    return inst;
}

void ExperimentBase::register_experiment(ExperimentBase* exp) {
    registry().push_back(exp);
}

bool ExperimentBase::try_run_experiment(const Args& args) {
    for (const auto& arg : args.unknown) {
        for (auto* exp : registry()) {
            if (arg == exp->flag()) {
                exp->run();
                return true;
            }
        }
    }
    return false;
}
