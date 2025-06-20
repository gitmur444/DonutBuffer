export module experiments.concurrent_vs_lockfree_experiment;

#include "experiments/experiment_base.h"

export class ConcurrentVsLockFreeExperiment : public ExperimentBase {
public:
    ConcurrentVsLockFreeExperiment();
    std::string flag() const override;
    void run() override;
};
