#pragma once
#include <string>
#include <cstdint>

/**
 * Configuration structure for ring buffer implementation.
 * Used for specifying buffer type and performance parameters.
 */
struct RingBufferConfig {
    // Тип буфера: "lockfree", "mutex", "concurrent_queue"
    std::string buffer_type = "lockfree";
    
    // Количество производителей
    int producer_count = 1;
    
    // Количество потребителей
    int consumer_count = 1;
    
    // Размер буфера в мегабайтах
    int buffer_size_mb = 1;
    
    // Общий объем данных для передачи в МБ
    uint64_t total_transfer_mb = 100;
};
