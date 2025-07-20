#pragma once

#include <gtest/gtest.h>
#include <string>
#include <chrono>

// Simple PostgreSQL logging for GTest 
// This version can actually connect to PostgreSQL when available

namespace SmartGTest {

class SimpleTestLogger : public ::testing::TestEventListener {
private:
    bool db_available = false;
    std::string test_suite;
    std::string test_name;
    std::chrono::steady_clock::time_point start_time;

public:
    SimpleTestLogger();

    // Required abstract methods from TestEventListener
    void OnTestProgramStart(const ::testing::UnitTest& unit_test) override;
    void OnTestIterationStart(const ::testing::UnitTest& unit_test, int iteration) override;
    void OnEnvironmentsSetUpStart(const ::testing::UnitTest& unit_test) override;
    void OnEnvironmentsSetUpEnd(const ::testing::UnitTest& unit_test) override;
    void OnTestPartResult(const ::testing::TestPartResult& test_part_result) override;
    void OnEnvironmentsTearDownStart(const ::testing::UnitTest& unit_test) override;
    void OnEnvironmentsTearDownEnd(const ::testing::UnitTest& unit_test) override;
    void OnTestIterationEnd(const ::testing::UnitTest& unit_test, int iteration) override;
    void OnTestProgramEnd(const ::testing::UnitTest& unit_test) override;

    void OnTestStart(const ::testing::TestInfo& test_info) override;
    void OnTestEnd(const ::testing::TestInfo& test_info) override;

private:
    void CheckDatabaseAvailability();
    void LogToActualTests(const std::string& suite, const std::string& name, 
                         const std::string& status, long duration_ms, 
                         const std::string& failure_msg);
};

// Helper function to register the Smart GTest listener
void RegisterSmartGTestListener();

// Macro for easy integration
#define SMART_GTEST_INIT() SmartGTest::RegisterSmartGTestListener()

} // namespace SmartGTest 