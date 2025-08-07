#include <iostream>

class VectorDemo {
public:
    void demonstrate() {
        std::cout << "=== Демонстрация size vs capacity ===\n\n";
        
        // Начальное состояние
        size_ = 0;
        capacity_ = 2;
        std::cout << "1. Начало: size=" << size_ << ", capacity=" << capacity_ << "\n";
        print_state();
        
        // Добавляем элементы
        push_back_demo(10);  // size=1, capacity=2
        push_back_demo(20);  // size=2, capacity=2 <- КРИТИЧЕСКИЙ МОМЕНТ!
        push_back_demo(30);  // size=3, нужно расширение!
    }
    
private:
    int* data_ = nullptr;
    size_t size_ = 0;
    size_t capacity_ = 0;
    
    void push_back_demo(int valueто что мы ) {
        std::cout << "\n🔸 Добавляем " << value << ":\n";
        std::cout << "   До: size=" << size_ << ", capacity=" << capacity_ << "\n";
        
        // ВОТ КЛЮЧЕВОЙ МОМЕНТ!
        if (size_ >= capacity_) {
            std::cout << "   ⚠️  size >= capacity (" << size_ << " >= " << capacity_ << ")\n";
            std::cout << "   📈 Нужно расширение!\n";
            
            size_t new_capacity = capacity_ == 0 ? 1 : capacity_ * 2;
            std::cout << "   🔄 Расширяем до " << new_capacity << "\n";
            capacity_ = new_capacity;
        } else {
            std::cout << "   ✅ Места достаточно (" << size_ << " < " << capacity_ << ")\n";
        }
        
        // Добавляем элемент
        ++size_;
        std::cout << "   После: size=" << size_ << ", capacity=" << capacity_ << "\n";
        print_state();
    }
    
    void print_state() {
        std::cout << "   Состояние: [";
        for (size_t i = 0; i < capacity_; ++i) {
            if (i < size_) {
                std::cout << "X";  // занято
            } else {
                std::cout << "_";  // свободно
            }
        }
        std::cout << "]\n";
    }
};

int main() {
    VectorDemo demo;
    demo.demonstrate();
    
    std::cout << "\n=== ОБЪЯСНЕНИЕ ===\n";
    std::cout << "size == capacity:  Последний слот занят, места НЕТ\n";
    std::cout << "size > capacity:   Ошибка! Не должно происходить\n";
    std::cout << "size < capacity:   Есть свободные слоты\n\n";
    
    std::cout << "ВЫВОД: size >= capacity защищает от ОБЕИХ проблем!\n";
    
    return 0;
} 