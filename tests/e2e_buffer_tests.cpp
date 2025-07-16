#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>
#include <cstdlib>
#include <regex>
#include <memory>

// Простая функция для выполнения команды и получения вывода
std::string exec_command(const std::string& cmd) {
    char buffer[128];
    std::string result = "";
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer, sizeof buffer, pipe.get()) != nullptr) {
        result += buffer;
    }
    return result;
}

// Класс для e2e тестирования BufferRunner
class BufferRunnerE2ETests {
private:
    std::string executable_path;
    
public:
    BufferRunnerE2ETests(const std::string& exe_path) : executable_path(exe_path) {}
    
    void test_default_parameters() {
        std::cout << "Testing default parameters..." << std::endl;
        
        std::string cmd = executable_path;
        std::string output = exec_command(cmd);
        
        // Проверяем, что программа запустилась и завершилась успешно
        assert(output.find("Running mutex with P=1 C=1") != std::string::npos);
        assert(output.find("Finished in") != std::string::npos);
        assert(output.find("items/sec") != std::string::npos);
        
        std::cout << "✓ Default parameters test passed" << std::endl;
    }
    
    void test_lockfree_type() {
        std::cout << "Testing lockfree type..." << std::endl;
        
        std::string cmd = executable_path + " --type=lockfree";
        std::string output = exec_command(cmd);
        
        assert(output.find("Running lockfree with P=1 C=1") != std::string::npos);
        assert(output.find("Finished in") != std::string::npos);
        
        std::cout << "✓ Lockfree type test passed" << std::endl;
    }
    
    void test_multiple_producers_consumers() {
        std::cout << "Testing multiple producers and consumers..." << std::endl;
        
        std::string cmd = executable_path + " --type=lockfree --producers=3 --consumers=2";
        std::string output = exec_command(cmd);
        
        assert(output.find("Running lockfree with P=3 C=2") != std::string::npos);
        assert(output.find("Finished in") != std::string::npos);
        
        std::cout << "✓ Multiple producers/consumers test passed" << std::endl;
    }
    
    void test_performance_reasonable() {
        std::cout << "Testing performance is reasonable..." << std::endl;
        
        std::string cmd = executable_path + " --type=lockfree --producers=2 --consumers=2";
        std::string output = exec_command(cmd);
        
        // Извлекаем количество items/sec из вывода
        std::regex perf_regex(R"((\d+(?:\.\d+)?(?:e\+?\d+)?)\s+items/sec)");
        std::smatch match;
        
        if (std::regex_search(output, match, perf_regex)) {
            double items_per_sec = std::stod(match[1].str());
            std::cout << "Performance: " << items_per_sec << " items/sec" << std::endl;
            
            // Проверяем, что производительность разумная (больше 10K items/sec)
            assert(items_per_sec > 10000.0);
            std::cout << "✓ Performance test passed" << std::endl;
        } else {
            std::cerr << "❌ Could not parse performance from output: " << output << std::endl;
            assert(false);
        }
    }
    
    void test_invalid_type() {
        std::cout << "Testing invalid buffer type..." << std::endl;
        
        std::string cmd = executable_path + " --type=invalid 2>&1";
        std::string output = exec_command(cmd);
        
        // При неизвестном типе программа должна использовать mutex по умолчанию
        // или выдать ошибку (в зависимости от реализации)
        assert(output.find("Running") != std::string::npos || 
               output.find("Unknown") != std::string::npos);
        
        std::cout << "✓ Invalid type test passed" << std::endl;
    }
    
    void test_stress_high_concurrency() {
        std::cout << "Testing high concurrency stress..." << std::endl;
        
        std::string cmd = executable_path + " --type=lockfree --producers=8 --consumers=8";
        std::string output = exec_command(cmd);
        
        assert(output.find("Running lockfree with P=8 C=8") != std::string::npos);
        assert(output.find("Finished in") != std::string::npos);
        
        // Проверяем, что время выполнения разумное (меньше 10 секунд)
        std::regex time_regex(R"(Finished in (\d+(?:\.\d+)?)\s+sec)");
        std::smatch match;
        
        if (std::regex_search(output, match, time_regex)) {
            double seconds = std::stod(match[1].str());
            std::cout << "Execution time: " << seconds << " seconds" << std::endl;
            assert(seconds < 10.0);
        }
        
        std::cout << "✓ High concurrency stress test passed" << std::endl;
    }
    
    void test_mutex_vs_lockfree_performance() {
        std::cout << "Testing mutex vs lockfree performance comparison..." << std::endl;
        
        // Тест с mutex
        std::string cmd_mutex = executable_path + " --type=mutex --producers=4 --consumers=4";
        std::string output_mutex = exec_command(cmd_mutex);
        
        // Тест с lockfree
        std::string cmd_lockfree = executable_path + " --type=lockfree --producers=4 --consumers=4";
        std::string output_lockfree = exec_command(cmd_lockfree);
        
        std::regex perf_regex(R"((\d+(?:\.\d+)?(?:e\+?\d+)?)\s+items/sec)");
        std::smatch match_mutex, match_lockfree;
        
        if (std::regex_search(output_mutex, match_mutex, perf_regex) &&
            std::regex_search(output_lockfree, match_lockfree, perf_regex)) {
            
            double mutex_perf = std::stod(match_mutex[1].str());
            double lockfree_perf = std::stod(match_lockfree[1].str());
            
            std::cout << "Mutex performance: " << mutex_perf << " items/sec" << std::endl;
            std::cout << "Lockfree performance: " << lockfree_perf << " items/sec" << std::endl;
            
            // Обычно lockfree должен быть быстрее, но не всегда
            // Просто проверяем, что оба работают с разумной производительностью
            assert(mutex_perf > 1000.0);
            assert(lockfree_perf > 1000.0);
            
            std::cout << "✓ Performance comparison test passed" << std::endl;
        } else {
            std::cerr << "❌ Could not parse performance from outputs" << std::endl;
            assert(false);
        }
    }
    
    void run_all_tests() {
        std::cout << "=== Running E2E Tests for BufferRunner ===" << std::endl;
        
        try {
            test_default_parameters();
            test_lockfree_type();
            test_multiple_producers_consumers();
            test_performance_reasonable();
            test_invalid_type();
            test_stress_high_concurrency();
            test_mutex_vs_lockfree_performance();
            
            std::cout << "\n🎉 All E2E tests passed!" << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "❌ Test failed with exception: " << e.what() << std::endl;
            std::exit(1);
        }
    }
};

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <path_to_BufferRunner_executable>" << std::endl;
        return 1;
    }
    
    std::string exe_path = argv[1];
    BufferRunnerE2ETests tests(exe_path);
    tests.run_all_tests();
    
    return 0;
} 