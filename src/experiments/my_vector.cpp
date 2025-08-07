#include <iostream>
#include <memory>
#include <stdexcept>
#include <algorithm>
#include <initializer_list>
#include <type_traits>
#include <chrono>
#include <cstdlib>

template<typename T>
class MyVector {
private:
    T* data_;
    size_t size_;
    size_t capacity_;
    
    // Алокатор для выровненной памяти (оптимизация)
    static constexpr size_t alignment = alignof(T);
    
public:
    // ✅ Конструкторы и деструктор (RAII)
    MyVector() noexcept : data_(nullptr), size_(0), capacity_(0) {}
    
    explicit MyVector(size_t initial_capacity) 
        : data_(nullptr), size_(0), capacity_(0) {
        reserve(initial_capacity);
    }
    
    MyVector(std::initializer_list<T> init) 
        : data_(nullptr), size_(0), capacity_(0) {
        reserve(init.size());
        for (const auto& item : init) {
            push_back(item);
        }
    }
    
    // Copy constructor
    MyVector(const MyVector& other) 
        : data_(nullptr), size_(0), capacity_(0) {
        reserve(other.capacity_);
        for (size_t i = 0; i < other.size_; ++i) {
            push_back(other.data_[i]);
        }
    }
    
    // Move constructor
    MyVector(MyVector&& other) noexcept 
        : data_(other.data_), size_(other.size_), capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }
    
    // Деструктор
    ~MyVector() {
        clear();
        deallocate();
    }
    
    // ✅ Assignment operators
    MyVector& operator=(const MyVector& other) {
        if (this != &other) {
            clear();
            reserve(other.capacity_);
            for (size_t i = 0; i < other.size_; ++i) {
                push_back(other.data_[i]);
            }
        }
        return *this;
    }
    
    MyVector& operator=(MyVector&& other) noexcept {
        if (this != &other) {
            clear();
            deallocate();
            
            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;
            
            other.data_ = nullptr;
            other.size_ = 0;
            other.capacity_ = 0;
        }
        return *this;
    }
    
    // ✅ ОСНОВНОЙ МЕТОД: reserve() - изменение емкости
    void reserve(size_t newCapacity) {
        if (newCapacity <= capacity_) {
            return; // Не уменьшаем capacity
        }
        
        // Выделяем новую память
        T* newData = allocate(newCapacity);
        
        // Перемещаем/копируем существующие элементы
        if (data_) {
            if constexpr (std::is_nothrow_move_constructible_v<T>) {
                // Используем move если доступно
                for (size_t i = 0; i < size_; ++i) {
                    new(newData + i) T(std::move(data_[i]));
                    data_[i].~T();
                }
            } else {
                // Fallback на copy
                for (size_t i = 0; i < size_; ++i) {
                    new(newData + i) T(data_[i]);
                    data_[i].~T();
                }
            }
        }
        
        // Освобождаем старую память
        deallocate();
        
        // Обновляем указатели
        data_ = newData;
        capacity_ = newCapacity;
    }
    
    // ✅ ОСНОВНОЙ МЕТОД: push_back() - добавление элемента
    void push_back(const T& value) {
        if (size_ >= capacity_) {
            // Стратегия роста: удваивание емкости (амортизированная O(1))
            size_t newCapacity = capacity_ == 0 ? 1 : capacity_ * 2;
            reserve(newCapacity);
        }
        
        // Размещаем новый элемент
        new(data_ + size_) T(value);
        ++size_;
    }
    
    // ✅ Move версия push_back
    void push_back(T&& value) {
        if (size_ >= capacity_) {
            size_t newCapacity = capacity_ == 0 ? 1 : capacity_ * 2;
            reserve(newCapacity);
        }
        
        new(data_ + size_) T(std::move(value));
        ++size_;
    }
    
    // ✅ Emplace - конструирование на месте
    template<typename... Args>
    void emplace_back(Args&&... args) {
        if (size_ >= capacity_) {
            size_t newCapacity = capacity_ == 0 ? 1 : capacity_ * 2;
            reserve(newCapacity);
        }
        
        new(data_ + size_) T(std::forward<Args>(args)...);
        ++size_;
    }
    
    // ✅ Основные методы доступа
    T& operator[](size_t index) noexcept {
        return data_[index];
    }
    
    const T& operator[](size_t index) const noexcept {
        return data_[index];
    }
    
    T& at(size_t index) {
        if (index >= size_) {
            throw std::out_of_range("Index out of range");
        }
        return data_[index];
    }
    
    const T& at(size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("Index out of range");
        }
        return data_[index];
    }
    
    // ✅ Информационные методы
    size_t size() const noexcept { return size_; }
    size_t capacity() const noexcept { return capacity_; }
    bool empty() const noexcept { return size_ == 0; }
    
    T* data() noexcept { return data_; }
    const T* data() const noexcept { return data_; }
    
    // ✅ Итераторы
    T* begin() noexcept { return data_; }
    T* end() noexcept { return data_ + size_; }
    const T* begin() const noexcept { return data_; }
    const T* end() const noexcept { return data_ + size_; }
    const T* cbegin() const noexcept { return data_; }
    const T* cend() const noexcept { return data_ + size_; }
    
    // ✅ Дополнительные методы
    void clear() {
        for (size_t i = 0; i < size_; ++i) {
            data_[i].~T();
        }
        size_ = 0;
    }
    
    void pop_back() {
        if (size_ > 0) {
            --size_;
            data_[size_].~T();
        }
    }
    
    void resize(size_t newSize) {
        if (newSize > size_) {
            reserve(newSize);
            for (size_t i = size_; i < newSize; ++i) {
                new(data_ + i) T();
            }
        } else {
            for (size_t i = newSize; i < size_; ++i) {
                data_[i].~T();
            }
        }
        size_ = newSize;
    }
    
    void shrink_to_fit() {
        if (size_ < capacity_) {
            MyVector temp(*this);
            *this = std::move(temp);
        }
    }

private:
    // ✅ Внутренние методы управления памятью
    T* allocate(size_t count) {
        if (count == 0) return nullptr;
        
        // Простая аллокация с проверкой переполнения
        size_t total_size = count * sizeof(T);
        if (total_size / sizeof(T) != count) {
            throw std::bad_alloc(); // Переполнение
        }
        
        T* ptr = static_cast<T*>(std::malloc(total_size));
        if (!ptr) {
            throw std::bad_alloc();
        }
        return ptr;
    }
    
    void deallocate() noexcept {
        if (data_) {
            std::free(data_);
            data_ = nullptr;
        }
    }
};

// ✅ Демонстрация и тесты
int main() {
    std::cout << "=== MyVector Demonstrations ===\n\n";
    
    // Тест 1: Основная функциональность
    std::cout << "1. Basic functionality:\n";
    MyVector<int> vec;
    std::cout << "   Initial size: " << vec.size() << ", capacity: " << vec.capacity() << "\n";
    
    // Добавляем элементы
    for (int i = 1; i <= 10; ++i) {
        vec.push_back(i);
        std::cout << "   After push_back(" << i << "): size=" << vec.size() 
                  << ", capacity=" << vec.capacity() << "\n";
    }
    
    // Тест 2: Reserve
    std::cout << "\n2. Reserve test:\n";
    MyVector<int> vec2;
    vec2.reserve(100);
    std::cout << "   After reserve(100): size=" << vec2.size() 
              << ", capacity=" << vec2.capacity() << "\n";
    
    for (int i = 0; i < 5; ++i) {
        vec2.push_back(i);
    }
    std::cout << "   After 5 push_backs: size=" << vec2.size() 
              << ", capacity=" << vec2.capacity() << "\n";
    
    // Тест 3: Initializer list
    std::cout << "\n3. Initializer list:\n";
    MyVector<std::string> vec3{"Hello", "World", "C++", "Templates"};
    std::cout << "   vec3 contents: ";
    for (const auto& str : vec3) {
        std::cout << str << " ";
    }
    std::cout << "\n   size=" << vec3.size() << ", capacity=" << vec3.capacity() << "\n";
    
    // Тест 4: Emplace
    std::cout << "\n4. Emplace test:\n";
    MyVector<std::pair<int, std::string>> vec4;
    vec4.emplace_back(1, "one");
    vec4.emplace_back(2, "two");
    vec4.emplace_back(3, "three");
    
    std::cout << "   vec4 contents: ";
    for (const auto& p : vec4) {
        std::cout << "{" << p.first << "," << p.second << "} ";
    }
    std::cout << "\n";
    
    // Тест 5: Performance comparison
    std::cout << "\n5. Performance test (1,000,000 elements):\n";
    
    auto start = std::chrono::high_resolution_clock::now();
    MyVector<int> perfVec;
    for (int i = 0; i < 1000000; ++i) {
        perfVec.push_back(i);
    }
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "   MyVector push_back 1M elements: " << duration.count() << " ms\n";
    std::cout << "   Final size: " << perfVec.size() << ", capacity: " << perfVec.capacity() << "\n";
    
    // Тест с reserve
    start = std::chrono::high_resolution_clock::now();
    MyVector<int> perfVec2;
    perfVec2.reserve(1000000);
    for (int i = 0; i < 1000000; ++i) {
        perfVec2.push_back(i);
    }
    end = std::chrono::high_resolution_clock::now();
    
    duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    std::cout << "   MyVector with reserve: " << duration.count() << " ms\n";
    
    std::cout << "\n🚀 MyVector implementation complete!\n";
    
    return 0;
} 