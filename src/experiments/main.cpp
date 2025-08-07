template<typename T>
class MyVector
{
public:
    void reserve(size_t newCapacity)
    {
        if (newCapacity <= capacity_) {
            return; // Не уменьшаем capacity
        }
        
        // Выделяем новую память
        T* newData = static_cast<T*>(std::malloc(newCapacity * sizeof(T)));
        if (!newData) {
            throw std::bad_alloc();
        }
        
        // Перемещаем/копируем существующие элементы
        if (data_) {
            for (size_t i = 0; i < size_; ++i) {
                new(newData + i) T(std::move(data_[i]));
                data_[i].~T();
            }
            std::free(data_);
        }
        
        // Обновляем указатели
        data_ = newData;
        capacity_ = newCapacity;
    }
    
    void push_back(const T& value)
    {
        if (size_ >= capacity_) {
            // Стратегия роста: удваивание емкости (амортизированная O(1))
            size_t newCapacity = capacity_ == 0 ? 1 : capacity_ * 2;
            reserve(newCapacity);
        }
        
        // Размещаем новый элемент
        new(data_ + size_) T(value);
        ++size_;
    }

private:
    T* data_ = nullptr;
    size_t size_ = 0;
    size_t capacity_ = 0;
}; 