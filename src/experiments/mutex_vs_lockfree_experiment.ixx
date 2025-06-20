export module experiments.mutex_vs_lockfree_experiment;

#include "experiments/experiment_base.h"

export class MutexVsLockFreeExperiment : public ExperimentBase {
public:
    MutexVsLockFreeExperiment();
    std::string flag() const override;
    void run() override;
};
