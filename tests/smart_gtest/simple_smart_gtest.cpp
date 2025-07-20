#include "simple_smart_gtest.h"
#include <iostream>
#include <memory>
#include <cstdlib>

namespace SmartGTest {

SimpleTestLogger::SimpleTestLogger() {
    // Check if PostgreSQL is available via environment or simple test
    CheckDatabaseAvailability();
}

// Required abstract methods from TestEventListener
void SimpleTestLogger::OnTestProgramStart(const ::testing::UnitTest& /*unit_test*/) {
    if (db_available) {
        std::cout << "[SMART] Database available - will log to PostgreSQL" << std::endl;
    } else {
        std::cout << "[SMART] Database not available - will log to console only" << std::endl;
    }
}

void SimpleTestLogger::OnTestIterationStart(const ::testing::UnitTest& /*unit_test*/, int /*iteration*/) {}
void SimpleTestLogger::OnEnvironmentsSetUpStart(const ::testing::UnitTest& /*unit_test*/) {}
void SimpleTestLogger::OnEnvironmentsSetUpEnd(const ::testing::UnitTest& /*unit_test*/) {}
void SimpleTestLogger::OnTestPartResult(const ::testing::TestPartResult& /*test_part_result*/) {}
void SimpleTestLogger::OnEnvironmentsTearDownStart(const ::testing::UnitTest& /*unit_test*/) {}
void SimpleTestLogger::OnEnvironmentsTearDownEnd(const ::testing::UnitTest& /*unit_test*/) {}
void SimpleTestLogger::OnTestIterationEnd(const ::testing::UnitTest& /*unit_test*/, int /*iteration*/) {}
void SimpleTestLogger::OnTestProgramEnd(const ::testing::UnitTest& /*unit_test*/) {}

void SimpleTestLogger::OnTestStart(const ::testing::TestInfo& test_info) {
    test_suite = test_info.test_suite_name();
    test_name = test_info.name();
    start_time = std::chrono::steady_clock::now();
    
    std::cout << "[SMART] Starting test: " << test_suite << "." << test_name << std::endl;
}

void SimpleTestLogger::OnTestEnd(const ::testing::TestInfo& test_info) {
    auto end_time = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::string status = test_info.result()->Passed() ? "PASSED" : "FAILED";
    std::string failure_message = "";
    
    if (!test_info.result()->Passed()) {
        // Collect failure information
        for (int i = 0; i < test_info.result()->total_part_count(); ++i) {
            auto& part = test_info.result()->GetTestPartResult(i);
            if (part.failed()) {
                failure_message += part.message();
                failure_message += " ";
            }
        }
    }
    
    std::cout << "[SMART] Test completed: " << test_suite << "." << test_name 
              << " - " << status << " (" << duration.count() << "ms)" << std::endl;
    
    // Log to actual_tests table
    LogToActualTests(test_suite, test_name, status, duration.count(), failure_message);
}

void SimpleTestLogger::CheckDatabaseAvailability() {
    // Проверка подключения к локальной PostgreSQL
    int result = std::system("psql -d testdb -c '\\q' >/dev/null 2>&1");
    db_available = (result == 0);
}

void SimpleTestLogger::LogToActualTests(const std::string& suite, const std::string& name, 
                     const std::string& status, long duration_ms, 
                     const std::string& failure_msg) {
    
    // Создаем описание теста на основе suite и имени
    std::string description = "Test: " + suite + "::" + name;
    if (status == "FAILED") {
        description += " (Performance/Functionality test that failed)";
    } else {
        description += " (Automated test execution)";
    }
    
    // Определяем теги на основе типа теста
    std::string tags;
    if (suite.find("Performance") != std::string::npos) {
        tags = "performance,benchmark";
    } else if (suite.find("Concurrent") != std::string::npos) {
        tags = "concurrency,multithreading";
    } else if (suite.find("Stress") != std::string::npos) {
        tags = "stress,load-testing";
    } else if (suite.find("Mutex") != std::string::npos) {
        tags = "mutex,synchronization";
    } else if (suite.find("LockFree") != std::string::npos) {
        tags = "lockfree,atomics";
    } else {
        tags = "unit,basic";
    }
    
    // Формируем SQL с полными данными и явными приведениями типов
    std::string sql = "SELECT upsert_actual_test_v2('" + suite + "'::VARCHAR(255), '" + name 
                     + "'::VARCHAR(255), '" + status + "'::VARCHAR(20), " + std::to_string(duration_ms) + "::INTEGER";
    
    if (!failure_msg.empty()) {
        // Escape single quotes in failure message
        std::string escaped_msg = failure_msg;
        size_t pos = 0;
        while ((pos = escaped_msg.find("'", pos)) != std::string::npos) {
            escaped_msg.replace(pos, 1, "''");
            pos += 2;
        }
        sql += ", '" + escaped_msg + "'::TEXT";
    } else {
        sql += ", NULL::TEXT";
    }
    
    // Добавляем description
    sql += ", '" + description + "'::TEXT";
    
    // Добавляем tags
    sql += ", '" + tags + "'::TEXT";
    
    // Добавляем временные метки
    sql += ", CURRENT_TIMESTAMP::TIMESTAMP";
    sql += ", (CURRENT_TIMESTAMP + INTERVAL '" + std::to_string(duration_ms) + " milliseconds')::TIMESTAMP";
    
    sql += ");";
    
    if (db_available) {
        // Выполняем SQL для локальной PostgreSQL
        std::string cmd = "psql -d testdb -c \"" + sql + "\" >/dev/null 2>&1";
        int result = std::system(cmd.c_str());
        if (result == 0) {
            std::cout << "[SMART] ✅ Logged to database: " << suite << "." << name << " - " << status 
                      << " (tags: " << tags << ")" << std::endl;
        } else {
            std::cout << "[SMART] ❌ Database logging failed for: " << suite << "." << name << std::endl;
        }
    } else {
        std::cout << "[SMART] Would execute SQL: " << sql << std::endl;
    }
}

// Helper function to register the Smart GTest listener
void RegisterSmartGTestListener() {
    ::testing::TestEventListeners& listeners = ::testing::UnitTest::GetInstance()->listeners();
    listeners.Append(new SimpleTestLogger());
}

} // namespace SmartGTest 