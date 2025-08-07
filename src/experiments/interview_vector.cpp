#include <memory>
#include <iostream>

template<typename T, typename Allocator = std::allocator<T>>
class MyVector {
public:
    void reserve(size_t newCapacity) {
        if (newCapacity <= capacity_) 
            return;
        
        T* newData = alloc_.allocate(newCapacity);
        
        // Move existing elements
        for (size_t i = 0; i < size_; ++i) {
            std::construct_at(newData + i, std::move(data_[i]));
            std::destroy_at(data_ + i);
        }
        
        if (data_) 
            alloc_.deallocate(data_, capacity_);
        
        data_ = newData;
        capacity_ = newCapacity;
    }
    
    void push_back(const T& value) {
        if (size_ >= capacity_) {
            reserve(capacity_ == 0 ? 1 : capacity_ * 2);
        }
        
        std::construct_at(data_ + size_, value);
        ++size_;
    }
    
    // Constructors
    MyVector() = default;
    
    // Rule of 5
    ~MyVector() {
        clear();
        if (data_) alloc_.deallocate(data_, capacity_);
    }
    
    MyVector(const MyVector&) = delete;
    MyVector& operator=(const MyVector&) = delete;
    
    MyVector(MyVector&& other) noexcept 
        : data_(other.data_), size_(other.size_), capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = other.capacity_ = 0;
    }
    
    MyVector& operator=(MyVector&& other) noexcept {
        if (this != &other) {
            clear();
            if (data_) alloc_.deallocate(data_, capacity_);
            
            data_ = other.data_;
            size_ = other.size_;
            capacity_ = other.capacity_;
            
            other.data_ = nullptr;
            other.size_ = other.capacity_ = 0;
        }
        return *this;
    }

private:
    T* data_ = nullptr;
    size_t size_ = 0;
    size_t capacity_ = 0;
    Allocator alloc_;
    
    void clear() {
        for (size_t i = 0; i < size_; ++i) {
            std::destroy_at(data_ + i);
        }
        size_ = 0;
    }
};

int main() {
    MyVector<int> v;
    v.push_back(123);
    
    std::cout << "✅ Interview-ready MyVector implementation\n";
    return 0;
} 