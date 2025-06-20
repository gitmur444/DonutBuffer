#pragma once
#include "experiment_base.h"

class ConcurrentVsLockfreeExperiment : public ExperimentBase {
public:
    ConcurrentVsLockfreeExperiment();
    void run() override;
    const char* flag() const override { return "--concurrent-vs-lockfree"; }
private:
    static ConcurrentVsLockfreeExperiment instance;
};
