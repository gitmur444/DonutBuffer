#pragma once
#include "experiment_base.h"

class MutexVsLockfreeExperiment : public ExperimentBase {
public:
    MutexVsLockfreeExperiment();
    void run() override;
    const char* flag() const override { return "--mutex-vs-lockfree"; }
private:
    static MutexVsLockfreeExperiment instance;
};
