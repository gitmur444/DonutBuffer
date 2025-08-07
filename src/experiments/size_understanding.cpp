#include <iostream>

template<typename T>
class VectorSizeDemo {
public:
    void demonstrate() {
        std::cout << "=== Capacity: элементы vs байты ===\n\n";
        
        std::cout << "sizeof(T) = " << sizeof(T) << " байт\n";
        std::cout << "capacity_ = " << capacity_ << " ЭЛЕМЕНТОВ\n";
        std::cout << "Общая память = " << capacity_ * sizeof(T) << " байт\n\n";
        
        // Демонстрация добавления элементов
        for (int i = 1; i <= 5; ++i) {
            push_back_demo(static_cast<T>(i * 10));
        }
    }

private:
    T* data_ = nullptr;
    size_t size_ = 0;
    size_t capacity_ = 2;  // 2 ЭЛЕМЕНТА, не байта!
    
    void push_back_demo(T value) {
        std::cout << "🔸 Добавляем элемент " << value << " (размер: " << sizeof(T) << " байт)\n";
        std::cout << "   size=" << size_ << ", capacity=" << capacity_ << " элементов\n";
        
        // КЛЮЧЕВОЙ МОМЕНТ: проверяем количество ЭЛЕМЕНТОВ!
        if (size_ >= capacity_) {
            std::cout << "   ❌ Места нет: " << size_ << " >= " << capacity_ << " элементов\n";
            std::cout << "   📈 Расширяем capacity с " << capacity_;
            capacity_ *= 2;
            std::cout << " до " << capacity_ << " элементов\n";
            std::cout << "   💾 Новая память: " << capacity_ * sizeof(T) << " байт\n";
        } else {
            std::cout << "   ✅ Места достаточно: " << size_ << " < " << capacity_ << " элементов\n";
        }
        
        ++size_;
        std::cout << "   Результат: size=" << size_ << ", capacity=" << capacity_ << "\n\n";
    }
};

// Демонстрация с разными типами
int main() {
    std::cout << "=== ВАЖНОЕ ПОНИМАНИЕ ===\n";
    std::cout << "capacity измеряется в ЭЛЕМЕНТАХ, не в байтах!\n\n";
    
    std::cout << "1. Vector<int>:\n";
    VectorSizeDemo<int> demo_int;
    demo_int.demonstrate();
    
    std::cout << "\n2. Vector<double>:\n";
    VectorSizeDemo<double> demo_double;
    demo_double.demonstrate();
    
    std::cout << "=== ОБЪЯСНЕНИЕ ===\n";
    std::cout << "• capacity = количество элементов типа T\n";
    std::cout << "• Каждый push_back добавляет ОДИН элемент\n";
    std::cout << "• Размер элемента не влияет на логику расширения\n";
    std::cout << "• Аллокатор уже знает sizeof(T)\n\n";
    
    std::cout << "ВЫВОД: size >= capacity - правильная проверка!\n";
    std::cout << "НЕ НУЖНО: size + 1 > capacity (избыточно)\n";
    std::cout << "НЕ НУЖНО: size * sizeof(T) >= capacity * sizeof(T)\n";
    
    return 0;
} 