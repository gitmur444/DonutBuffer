-- Smart GTest Database Schema
-- Database for storing test execution results and analytics

-- Таблица для хранения всех результатов тестов (историческая)
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_suite VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PASSED', 'FAILED', 'SKIPPED')),
    execution_time_ms INTEGER,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    failure_message TEXT,
    description TEXT,
    tags TEXT,
    
    UNIQUE(test_suite, test_name, start_time)
);

-- Новая таблица для актуальных тестов в кодовой базе
CREATE TABLE IF NOT EXISTS actual_tests (
    id SERIAL PRIMARY KEY,
    test_suite VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PASSED', 'FAILED', 'SKIPPED')),
    execution_time_ms INTEGER,
    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_message TEXT,
    description TEXT,
    tags TEXT,
    run_count INTEGER DEFAULT 1,
    
    UNIQUE(test_suite, test_name)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_test_results_suite_name ON test_results(test_suite, test_name);
CREATE INDEX IF NOT EXISTS idx_test_results_status ON test_results(status);
CREATE INDEX IF NOT EXISTS idx_test_results_start_time ON test_results(start_time);

CREATE INDEX IF NOT EXISTS idx_actual_tests_suite_name ON actual_tests(test_suite, test_name);
CREATE INDEX IF NOT EXISTS idx_actual_tests_status ON actual_tests(status);
CREATE INDEX IF NOT EXISTS idx_actual_tests_last_run ON actual_tests(last_run);

-- Представления для аналитики

-- Статистика по историческим тестам
CREATE OR REPLACE VIEW test_stats AS
SELECT 
    test_suite,
    test_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'PASSED' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_count,
    SUM(CASE WHEN status = 'SKIPPED' THEN 1 ELSE 0 END) as skipped_count,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms,
    MAX(start_time) as last_execution
FROM test_results 
GROUP BY test_suite, test_name;

-- Последние запуски тестов
CREATE OR REPLACE VIEW recent_test_runs AS
SELECT 
    test_suite,
    test_name,
    status,
    execution_time_ms,
    start_time,
    failure_message,
    description,
    tags
FROM test_results 
WHERE start_time >= NOW() - INTERVAL '1 DAY'
ORDER BY start_time DESC;

-- Актуальное состояние тестов в кодовой базе
CREATE OR REPLACE VIEW current_test_status AS
SELECT 
    test_suite,
    test_name,
    status,
    execution_time_ms,
    last_run,
    failure_message,
    description,
    tags,
    run_count,
    CASE 
        WHEN status = 'PASSED' THEN '✅'
        WHEN status = 'FAILED' THEN '❌'
        WHEN status = 'SKIPPED' THEN '⏭️'
    END as status_icon
FROM actual_tests 
ORDER BY test_suite, test_name;

-- Сводка по актуальным тестам
CREATE OR REPLACE VIEW actual_tests_summary AS
SELECT 
    COUNT(*) as total_tests,
    SUM(CASE WHEN status = 'PASSED' THEN 1 ELSE 0 END) as passed_tests,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_tests,
    SUM(CASE WHEN status = 'SKIPPED' THEN 1 ELSE 0 END) as skipped_tests,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms,
    COUNT(DISTINCT test_suite) as test_suites_count
FROM actual_tests;

-- Функция для очистки актуальных тестов (вызывается перед запуском набора тестов)
CREATE OR REPLACE FUNCTION clear_actual_tests()
RETURNS VOID AS $$
BEGIN
    DELETE FROM actual_tests;
    RAISE NOTICE 'Cleared actual_tests table for new test run';
END;
$$ LANGUAGE plpgsql;

-- Функция для добавления/обновления актуального теста
CREATE OR REPLACE FUNCTION upsert_actual_test(
    p_test_suite VARCHAR(255),
    p_test_name VARCHAR(255),
    p_status VARCHAR(20),
    p_execution_time_ms INTEGER DEFAULT NULL,
    p_failure_message TEXT DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_tags TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO actual_tests (
        test_suite, test_name, status, execution_time_ms, 
        last_run, failure_message, description, tags, run_count
    ) VALUES (
        p_test_suite, p_test_name, p_status, p_execution_time_ms, 
        CURRENT_TIMESTAMP, p_failure_message, p_description, p_tags, 1
    )
    ON CONFLICT (test_suite, test_name) 
    DO UPDATE SET
        status = EXCLUDED.status,
        execution_time_ms = EXCLUDED.execution_time_ms,
        last_run = EXCLUDED.last_run,
        failure_message = EXCLUDED.failure_message,
        description = EXCLUDED.description,
        tags = EXCLUDED.tags,
        run_count = actual_tests.run_count + 1;
END;
$$ LANGUAGE plpgsql;

-- Демонстрационные данные
INSERT INTO test_results (test_suite, test_name, status, execution_time_ms, description, tags) VALUES
('RingBufferTests', 'TestBasicOperations', 'PASSED', 15, 'Basic push/pop operations', 'basic,core'),
('RingBufferTests', 'TestCapacityHandling', 'PASSED', 8, 'Capacity and overflow handling', 'capacity,edge-case'),
('RingBufferTests', 'TestThreadSafety', 'FAILED', 150, 'Multi-threaded access test', 'threading,concurrent'),
('PerformanceTests', 'BenchmarkPushPop', 'PASSED', 2500, 'Push/pop performance benchmark', 'performance,benchmark'),
('PerformanceTests', 'BenchmarkMemoryUsage', 'PASSED', 1200, 'Memory usage analysis', 'performance,memory');

-- Демонстрационные актуальные тесты
INSERT INTO actual_tests (test_suite, test_name, status, execution_time_ms, description, tags) VALUES
('RingBufferTests', 'TestBasicOperations', 'PASSED', 15, 'Basic push/pop operations', 'basic,core'),
('RingBufferTests', 'TestCapacityHandling', 'PASSED', 8, 'Capacity and overflow handling', 'capacity,edge-case'),
('RingBufferTests', 'TestThreadSafety', 'FAILED', 150, 'Multi-threaded access test', 'threading,concurrent'),
('PerformanceTests', 'BenchmarkPushPop', 'PASSED', 2500, 'Push/pop performance benchmark', 'performance,benchmark'); 