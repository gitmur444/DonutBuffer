#include <vector>
#include <algorithm>
#include <ranges>
#include <iostream>
#include <chrono>
#include <random>

// ❌ НЕЭФФЕКТИВНЫЙ способ - O(n²)
void remove_even_naive(std::vector<int>& vec) {
    for (auto it = vec.begin(); it != vec.end();) {
        if (*it % 2 == 0) {
            it = vec.erase(it);  // erase() сдвигает все элементы -> O(n²)
        } else {
            ++it;
        }
    }
}

// ✅ ЭФФЕКТИВНЫЙ способ #1: erase-remove idiom - O(n)
void remove_even_erase_remove(std::vector<int>& vec) {
    vec.erase(
        std::remove_if(vec.begin(), vec.end(), 
                      [](int x) { return x % 2 == 0; }),
        vec.end()
    );
}

// ✅ ЭФФЕКТИВНЫЙ способ #2: C++20 ranges - O(n)
void remove_even_ranges(std::vector<int>& vec) {
    auto new_end = std::ranges::remove_if(vec, [](int x) { return x % 2 == 0; });
    vec.erase(new_end.begin(), vec.end());
}

// ✅ ЭФФЕКТИВНЫЙ способ #3: копирование - O(n)
std::vector<int> remove_even_copy(const std::vector<int>& vec) {
    std::vector<int> result;
    result.reserve(vec.size());  // оптимизация памяти
    
    std::ranges::copy_if(vec, std::back_inserter(result), 
                        [](int x) { return x % 2 != 0; });
    return result;
}

// ✅ САМЫЙ ЭФФЕКТИВНЫЙ: in-place с индексами - O(n)
void remove_even_in_place(std::vector<int>& vec) {
    size_t write_pos = 0;
    
    for (size_t read_pos = 0; read_pos < vec.size(); ++read_pos) {
        if (vec[read_pos] % 2 != 0) {  // если нечетный - оставляем
            vec[write_pos++] = vec[read_pos];
        }
    }
    
    vec.resize(write_pos);  // обрезаем до нужного размера
}

// Утилита для тестирования
void print_vector(const std::vector<int>& vec, const std::string& name) {
    std::cout << name << ": ";
    for (int x : vec) {
        std::cout << x << " ";
    }
    std::cout << "(size: " << vec.size() << ")\n";
}

// Генератор тестовых данных
std::vector<int> generate_test_data(size_t size) {
    std::vector<int> vec;
    vec.reserve(size);
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    
    for (size_t i = 0; i < size; ++i) {
        vec.push_back(dis(gen));
    }
    
    return vec;
}

// Бенчмарк
template<typename Func>
auto benchmark(Func&& func, std::vector<int> vec, const std::string& name) {
    auto start = std::chrono::high_resolution_clock::now();
    func(vec);
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << name << ": " << duration.count() << " μs\n";
    
    return vec;
}

int main() {
    // Демонстрация на небольшом примере
    std::cout << "=== Демонстрация на маленьком векторе ===\n";
    std::vector<int> demo_vec = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    print_vector(demo_vec, "Исходный");
    
    auto vec1 = demo_vec;
    remove_even_erase_remove(vec1);
    print_vector(vec1, "Erase-remove");
    
    auto vec2 = demo_vec;
    remove_even_ranges(vec2);
    print_vector(vec2, "C++20 ranges");
    
    auto vec3 = remove_even_copy(demo_vec);
    print_vector(vec3, "Copy");
    
    auto vec4 = demo_vec;
    remove_even_in_place(vec4);
    print_vector(vec4, "In-place");
    
    // Бенчмарк на больших данных
    std::cout << "\n=== Бенчмарк производительности (100,000 элементов) ===\n";
    const size_t test_size = 100000;
    auto test_data = generate_test_data(test_size);
    
    std::cout << "Исходный размер: " << test_data.size() << " элементов\n\n";
    
    auto result1 = benchmark([](std::vector<int>& v) { remove_even_erase_remove(v); }, 
                            test_data, "Erase-remove");
    
    auto result2 = benchmark([](std::vector<int>& v) { remove_even_ranges(v); }, 
                            test_data, "C++20 ranges");
    
    auto result3 = benchmark([](std::vector<int> v) -> std::vector<int> { return remove_even_copy(v); }, 
                            test_data, "Copy method");
    
    auto result4 = benchmark([](std::vector<int>& v) { remove_even_in_place(v); }, 
                            test_data, "In-place");
    
    // Показываем результирующие размеры
    std::cout << "\nРезультирующий размер: " << result1.size() << " элементов\n";
    
    std::cout << "\n🎯 Рекомендация: используйте in-place метод для максимальной производительности!\n";
    
    return 0;
} 